"""Linear Bytecode Compiler for the SMC Language.

Transforms AST trees into a flat instruction array for fast stack VM execution,
eliminating recursive tree-walking overhead on large loops and datasets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from smc.parser import (
    AstNode,
    BinaryOpNode,
    CompoundAssignNode,
    DictNode,
    ExpressionStatementNode,
    ForInNode,
    FunctionCallNode,
    FunctionDefNode,
    HaltNode,
    IfNode,
    IndexAccessNode,
    IndexAssignNode,
    ListNode,
    LiteralNode,
    PrintNode,
    ProgramNode,
    ReturnNode,
    SetVarNode,
    UnaryOpNode,
    VariableNode,
    WhileNode,
)


class BytecodeOp(str, Enum):
    LOAD_CONST = "LOAD_CONST"
    LOAD_VAR = "LOAD_VAR"
    STORE_VAR = "STORE_VAR"
    COMPOUND_ASSIGN = "COMPOUND_ASSIGN"
    BINARY_OP = "BINARY_OP"
    UNARY_OP = "UNARY_OP"
    BUILD_LIST = "BUILD_LIST"
    BUILD_DICT = "BUILD_DICT"
    INDEX_GET = "INDEX_GET"
    INDEX_SET = "INDEX_SET"
    JUMP = "JUMP"
    JUMP_IF_FALSE = "JUMP_IF_FALSE"
    CALL_BUILTIN = "CALL_BUILTIN"
    CALL_USER_FN = "CALL_USER_FN"
    PRINT = "PRINT"
    RETURN = "RETURN"
    POP_TOP = "POP_TOP"
    HALT = "HALT"


@dataclass
class Instruction:
    op: BytecodeOp
    operand: Any = None
    line: int = 0

    def __repr__(self) -> str:
        op_str = f" {self.operand!r}" if self.operand is not None else ""
        return f"{self.op.value:<16}{op_str}"


@dataclass
class BytecodeFunction:
    name: str
    params: list[str]
    code: list[Instruction] = field(default_factory=list)


@dataclass
class BytecodeChunk:
    instructions: list[Instruction] = field(default_factory=list)
    constants: list[Any] = field(default_factory=list)
    functions: dict[str, BytecodeFunction] = field(default_factory=dict)

    def emit(self, op: BytecodeOp, operand: Any = None, line: int = 0) -> int:
        idx = len(self.instructions)
        self.instructions.append(Instruction(op=op, operand=operand, line=line))
        return idx


class BytecodeCompiler:
    """Compiles AST ProgramNode into a flat BytecodeChunk."""

    def __init__(self) -> None:
        self.chunk = BytecodeChunk()

    def compile(self, program: ProgramNode) -> BytecodeChunk:
        for stmt in program.statements:
            self._compile_statement(stmt, self.chunk.instructions)
        self.chunk.emit(BytecodeOp.HALT)
        return self.chunk

    def _compile_statement(self, node: AstNode, instructions: list[Instruction]) -> None:
        if isinstance(node, SetVarNode):
            self._compile_expression(node.expr, instructions)
            instructions.append(Instruction(BytecodeOp.STORE_VAR, node.name))

        elif isinstance(node, CompoundAssignNode):
            self._compile_expression(node.expr, instructions)
            instructions.append(Instruction(BytecodeOp.COMPOUND_ASSIGN, (node.name, node.op)))

        elif isinstance(node, IndexAssignNode):
            instructions.append(Instruction(BytecodeOp.LOAD_VAR, node.target_name))
            self._compile_expression(node.index_expr, instructions)
            self._compile_expression(node.value_expr, instructions)
            instructions.append(Instruction(BytecodeOp.INDEX_SET, node.op))

        elif isinstance(node, PrintNode):
            self._compile_expression(node.expr, instructions)
            instructions.append(Instruction(BytecodeOp.PRINT))

        elif isinstance(node, ExpressionStatementNode):
            self._compile_expression(node.expr, instructions)
            instructions.append(Instruction(BytecodeOp.POP_TOP))

        elif isinstance(node, IfNode):
            self._compile_expression(node.condition, instructions)
            jump_false_idx = len(instructions)
            instructions.append(Instruction(BytecodeOp.JUMP_IF_FALSE, -1))

            for s in node.then_branch:
                self._compile_statement(s, instructions)

            if node.else_branch:
                jump_end_idx = len(instructions)
                instructions.append(Instruction(BytecodeOp.JUMP, -1))
                
                # Patch jump_if_false target
                instructions[jump_false_idx].operand = len(instructions)

                for s in node.else_branch:
                    self._compile_statement(s, instructions)

                # Patch jump_end target
                instructions[jump_end_idx].operand = len(instructions)
            else:
                instructions[jump_false_idx].operand = len(instructions)

        elif isinstance(node, WhileNode):
            loop_start = len(instructions)
            self._compile_expression(node.condition, instructions)
            jump_exit_idx = len(instructions)
            instructions.append(Instruction(BytecodeOp.JUMP_IF_FALSE, -1))

            for s in node.body:
                self._compile_statement(s, instructions)

            instructions.append(Instruction(BytecodeOp.JUMP, loop_start))
            instructions[jump_exit_idx].operand = len(instructions)

        elif isinstance(node, ForInNode):
            # Evaluate collection and store in ephemeral iterator variable
            self._compile_expression(node.collection_expr, instructions)
            # In bytecode VM, we can expand for-in or compile to a loop
            instructions.append(Instruction(BytecodeOp.STORE_VAR, f"__coll_{node.item_name}"))
            instructions.append(Instruction(BytecodeOp.LOAD_CONST, 0))
            instructions.append(Instruction(BytecodeOp.STORE_VAR, f"__idx_{node.item_name}"))

            loop_start = len(instructions)
            instructions.append(Instruction(BytecodeOp.LOAD_VAR, f"__idx_{node.item_name}"))
            instructions.append(Instruction(BytecodeOp.LOAD_VAR, f"__coll_{node.item_name}"))
            instructions.append(Instruction(BytecodeOp.CALL_BUILTIN, ("len", 1)))
            instructions.append(Instruction(BytecodeOp.BINARY_OP, "<"))
            jump_exit_idx = len(instructions)
            instructions.append(Instruction(BytecodeOp.JUMP_IF_FALSE, -1))

            # item = coll[idx]
            instructions.append(Instruction(BytecodeOp.LOAD_VAR, f"__coll_{node.item_name}"))
            instructions.append(Instruction(BytecodeOp.LOAD_VAR, f"__idx_{node.item_name}"))
            instructions.append(Instruction(BytecodeOp.INDEX_GET))
            instructions.append(Instruction(BytecodeOp.STORE_VAR, node.item_name))

            for s in node.body:
                self._compile_statement(s, instructions)

            # idx += 1
            instructions.append(Instruction(BytecodeOp.LOAD_CONST, 1))
            instructions.append(Instruction(BytecodeOp.COMPOUND_ASSIGN, (f"__idx_{node.item_name}", "+=")))
            instructions.append(Instruction(BytecodeOp.JUMP, loop_start))
            instructions[jump_exit_idx].operand = len(instructions)

        elif isinstance(node, FunctionDefNode):
            fn_code: list[Instruction] = []
            for s in node.body:
                self._compile_statement(s, fn_code)
            fn_code.append(Instruction(BytecodeOp.LOAD_CONST, 0))
            fn_code.append(Instruction(BytecodeOp.RETURN))
            self.chunk.functions[node.name] = BytecodeFunction(
                name=node.name, params=node.params, code=fn_code
            )

        elif isinstance(node, ReturnNode):
            self._compile_expression(node.expr, instructions)
            instructions.append(Instruction(BytecodeOp.RETURN))

        elif isinstance(node, HaltNode):
            instructions.append(Instruction(BytecodeOp.HALT))

    def _compile_expression(self, node: AstNode, instructions: list[Instruction]) -> None:
        if isinstance(node, LiteralNode):
            instructions.append(Instruction(BytecodeOp.LOAD_CONST, node.value))

        elif isinstance(node, VariableNode):
            instructions.append(Instruction(BytecodeOp.LOAD_VAR, node.name))

        elif isinstance(node, ListNode):
            for elem in node.elements:
                self._compile_expression(elem, instructions)
            instructions.append(Instruction(BytecodeOp.BUILD_LIST, len(node.elements)))

        elif isinstance(node, DictNode):
            for k_expr, v_expr in node.pairs:
                self._compile_expression(k_expr, instructions)
                self._compile_expression(v_expr, instructions)
            instructions.append(Instruction(BytecodeOp.BUILD_DICT, len(node.pairs)))

        elif isinstance(node, IndexAccessNode):
            self._compile_expression(node.target, instructions)
            self._compile_expression(node.index_expr, instructions)
            instructions.append(Instruction(BytecodeOp.INDEX_GET))

        elif isinstance(node, UnaryOpNode):
            self._compile_expression(node.operand, instructions)
            instructions.append(Instruction(BytecodeOp.UNARY_OP, node.op))

        elif isinstance(node, BinaryOpNode):
            self._compile_expression(node.left, instructions)
            self._compile_expression(node.right, instructions)
            instructions.append(Instruction(BytecodeOp.BINARY_OP, node.op))

        elif isinstance(node, FunctionCallNode):
            for arg in node.args:
                self._compile_expression(arg, instructions)
            # Differentiate user fn vs builtin
            instructions.append(Instruction(BytecodeOp.CALL_BUILTIN, (node.name, len(node.args))))

"""Flat Stack Virtual Machine (BytecodeVM) for compiled SMC Bytecode.

Executes linear instruction arrays on a high-speed operand stack with an integer
program counter (pc), achieving significantly higher execution throughput than AST tree-walkers.
"""

from __future__ import annotations

from typing import Any
from smc.compiler import BytecodeChunk, BytecodeOp, Instruction
from smc.vm import DexterVM


class BytecodeVM:
    """Fast flat stack-based virtual machine for compiled SMC bytecode."""

    def __init__(self) -> None:
        self.stack: list[Any] = []
        self.globals: dict[str, Any] = {}
        self.call_stack: list[dict[str, Any]] = []
        self.stdout: list[str] = []
        self.instructions_executed: int = 0
        self.dexter_helper = DexterVM()  # For built-in standard library delegation

    def run(self, chunk: BytecodeChunk) -> dict[str, Any]:
        self._execute_instructions(chunk.instructions, chunk)
        return {
            "final_variables": self.globals,
            "stdout": self.stdout,
            "instructions_executed": self.instructions_executed,
        }

    def _execute_instructions(self, code: list[Instruction], chunk: BytecodeChunk) -> Any:
        pc = 0
        code_len = len(code)

        while pc < code_len:
            inst = code[pc]
            op = inst.op
            operand = inst.operand
            self.instructions_executed += 1
            pc += 1

            if op == BytecodeOp.LOAD_CONST:
                self.stack.append(operand)

            elif op == BytecodeOp.LOAD_VAR:
                # Check local stack frame first, then globals
                val = 0
                if self.call_stack and operand in self.call_stack[-1]:
                    val = self.call_stack[-1][operand]
                elif operand in self.globals:
                    val = self.globals[operand]
                self.stack.append(val)

            elif op == BytecodeOp.STORE_VAR:
                val = self.stack.pop() if self.stack else 0
                if self.call_stack:
                    self.call_stack[-1][operand] = val
                else:
                    self.globals[operand] = val

            elif op == BytecodeOp.COMPOUND_ASSIGN:
                name, assign_op = operand
                rhs = self.stack.pop() if self.stack else 0
                curr = 0
                if self.call_stack and name in self.call_stack[-1]:
                    curr = self.call_stack[-1][name]
                elif name in self.globals:
                    curr = self.globals[name]

                if assign_op == "+=":
                    if isinstance(curr, str) or isinstance(rhs, str):
                        new_val = str(curr) + str(rhs)
                    elif isinstance(curr, list) and isinstance(rhs, list):
                        new_val = curr + rhs
                    else:
                        new_val = curr + rhs
                elif assign_op == "-=":
                    new_val = curr - rhs
                elif assign_op == "*=":
                    new_val = curr * rhs
                elif assign_op == "/=":
                    new_val = curr / rhs if rhs != 0 else 0
                else:
                    new_val = rhs

                if self.call_stack:
                    self.call_stack[-1][name] = new_val
                else:
                    self.globals[name] = new_val

            elif op == BytecodeOp.BINARY_OP:
                right = self.stack.pop() if self.stack else 0
                left = self.stack.pop() if self.stack else 0
                
                if operand == "+":
                    if isinstance(left, str) or isinstance(right, str):
                        self.stack.append(str(left) + str(right))
                    elif isinstance(left, list) and isinstance(right, list):
                        self.stack.append(left + right)
                    else:
                        self.stack.append(left + right)
                elif operand == "-":
                    self.stack.append(left - right)
                elif operand == "*":
                    self.stack.append(left * right)
                elif operand == "/":
                    self.stack.append(left / right if right != 0 else 0)
                elif operand == "%":
                    self.stack.append(left % right if right != 0 else 0)
                elif operand == "==":
                    self.stack.append(left == right)
                elif operand == "!=":
                    self.stack.append(left != right)
                elif operand == "<":
                    self.stack.append(left < right)
                elif operand == "<=":
                    self.stack.append(left <= right)
                elif operand == ">":
                    self.stack.append(left > right)
                elif operand == ">=":
                    self.stack.append(left >= right)
                elif operand in ("&&", "and"):
                    self.stack.append(bool(left) and bool(right))
                elif operand in ("||", "or"):
                    self.stack.append(bool(left) or bool(right))

            elif op == BytecodeOp.UNARY_OP:
                val = self.stack.pop() if self.stack else 0
                if operand == "-":
                    self.stack.append(-val)
                elif operand == "!":
                    self.stack.append(not bool(val))

            elif op == BytecodeOp.BUILD_LIST:
                count = int(operand)
                items = []
                for _ in range(count):
                    items.append(self.stack.pop())
                items.reverse()
                self.stack.append(items)

            elif op == BytecodeOp.BUILD_DICT:
                count = int(operand)
                pairs = []
                for _ in range(count):
                    v = self.stack.pop()
                    k = self.stack.pop()
                    pairs.append((k, v))
                pairs.reverse()
                self.stack.append(dict(pairs))

            elif op == BytecodeOp.INDEX_GET:
                idx = self.stack.pop() if self.stack else 0
                target = self.stack.pop() if self.stack else 0
                if isinstance(target, dict):
                    self.stack.append(target.get(idx, 0))
                elif isinstance(target, (list, str)):
                    try:
                        self.stack.append(target[int(idx)])
                    except (IndexError, TypeError, ValueError):
                        self.stack.append(0)
                else:
                    self.stack.append(0)

            elif op == BytecodeOp.INDEX_SET:
                val = self.stack.pop() if self.stack else 0
                idx = self.stack.pop() if self.stack else 0
                target = self.stack.pop() if self.stack else {}
                if isinstance(target, dict):
                    target[idx] = val
                elif isinstance(target, list):
                    try:
                        target[int(idx)] = val
                    except (IndexError, ValueError):
                        pass

            elif op == BytecodeOp.JUMP:
                pc = int(operand)

            elif op == BytecodeOp.JUMP_IF_FALSE:
                cond = self.stack.pop() if self.stack else False
                if not bool(cond):
                    pc = int(operand)

            elif op == BytecodeOp.CALL_BUILTIN:
                fn_name, argc = operand
                args = []
                for _ in range(argc):
                    args.append(self.stack.pop())
                args.reverse()

                # If user defined function
                if fn_name in chunk.functions:
                    fn_def = chunk.functions[fn_name]
                    frame = dict(zip(fn_def.params, args))
                    self.call_stack.append(frame)
                    ret_val = self._execute_instructions(fn_def.code, chunk)
                    self.call_stack.pop()
                    self.stack.append(ret_val)
                elif self.dexter_helper._is_builtin(fn_name):
                    res = self.dexter_helper._call_builtin(fn_name, args)
                    self.stack.append(res)
                else:
                    self.stack.append(0)

            elif op == BytecodeOp.PRINT:
                val = self.stack.pop() if self.stack else ""
                self.stdout.append(str(val))

            elif op == BytecodeOp.POP_TOP:
                if self.stack:
                    self.stack.pop()

            elif op == BytecodeOp.RETURN:
                return self.stack.pop() if self.stack else 0

            elif op == BytecodeOp.HALT:
                break

        return 0


def disassemble_chunk(chunk: BytecodeChunk, title: str = "BYTECODE DISASSEMBLY") -> str:
    """Generate human-readable bytecode disassembly listing."""
    lines = [
        f"; ==================================================================",
        f"; {title}",
        f"; Total Instructions: {len(chunk.instructions):,}",
        f"; ==================================================================",
        f"{'ADDR':<6} {'OPCODE':<18} {'OPERAND'}",
        "-" * 50,
    ]
    for idx, inst in enumerate(chunk.instructions):
        op_str = f" {inst.operand!r}" if inst.operand is not None else ""
        lines.append(f"{idx:04d}   {inst.op.value:<18}{op_str}")

    if chunk.functions:
        lines.append("\n; --- USER FUNCTIONS ---")
        for fn_name, fn in chunk.functions.items():
            lines.append(f"\nFunction: {fn_name}({', '.join(fn.params)}):")
            for f_idx, f_inst in enumerate(fn.code):
                op_str = f" {f_inst.operand!r}" if f_inst.operand is not None else ""
                lines.append(f"  {f_idx:04d}   {f_inst.op.value:<18}{op_str}")

    return "\n".join(lines)

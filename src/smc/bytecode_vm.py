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

    def __init__(self, strict_mode: bool = False) -> None:
        self.strict_mode: bool = strict_mode
        self.stack: list[Any] = []
        self.globals: dict[str, Any] = {}
        self.call_stack: list[dict[str, Any]] = []
        self.stdout: list[str] = []
        self.instructions_executed: int = 0
        self.dexter_helper = DexterVM(strict_mode=strict_mode)  # For built-in standard library delegation

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
        stack = self.stack
        stack_append = stack.append
        stack_pop = stack.pop
        globals_dict = self.globals
        call_stack = self.call_stack

        if len(call_stack) > 500:
            raise RecursionError("[STACK OVERFLOW] Maximum call stack depth of 500 exceeded in BytecodeVM")

        while pc < code_len:
            inst = code[pc]
            op = inst.op
            operand = inst.operand
            self.instructions_executed += 1
            pc += 1

            if op == BytecodeOp.LOAD_CONST:
                stack_append(operand)

            elif op == BytecodeOp.LOAD_VAR:
                # Check local stack frame first, then globals
                val = 0
                found = False
                if call_stack and operand in call_stack[-1]:
                    val = call_stack[-1][operand]
                    found = True
                elif operand in globals_dict:
                    val = globals_dict[operand]
                    found = True
                
                if not found and self.strict_mode:
                    raise NameError(f"Undefined identifier '{operand}' in BytecodeVM runtime")
                stack_append(val)

            elif op == BytecodeOp.STORE_VAR:
                val = stack_pop() if stack else 0
                if call_stack:
                    call_stack[-1][operand] = val
                else:
                    globals_dict[operand] = val

            elif op == BytecodeOp.COMPOUND_ASSIGN:
                name, assign_op = operand
                rhs = stack_pop() if stack else 0
                curr = 0
                if call_stack and name in call_stack[-1]:
                    curr = call_stack[-1][name]
                elif name in globals_dict:
                    curr = globals_dict[name]

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
                    if rhs == 0:
                        if self.strict_mode:
                            raise ZeroDivisionError("Division by zero in compound assignment")
                        new_val = 0
                    else:
                        new_val = curr / rhs
                else:
                    new_val = rhs

                if call_stack:
                    call_stack[-1][name] = new_val
                else:
                    globals_dict[name] = new_val

            elif op == BytecodeOp.BINARY_OP:
                right = stack_pop() if stack else 0
                left = stack_pop() if stack else 0
                
                if operand == "+":
                    if isinstance(left, str) or isinstance(right, str):
                        stack_append(str(left) + str(right))
                    elif isinstance(left, list) and isinstance(right, list):
                        stack_append(left + right)
                    else:
                        stack_append(left + right)
                elif operand == "-":
                    stack_append(left - right)
                elif operand == "*":
                    stack_append(left * right)
                elif operand == "/":
                    if right == 0:
                        if self.strict_mode:
                            raise ZeroDivisionError("Division by zero in BytecodeVM runtime")
                        stack_append(0)
                    else:
                        stack_append(left / right)
                elif operand == "%":
                    if right == 0:
                        if self.strict_mode:
                            raise ZeroDivisionError("Modulo by zero in BytecodeVM runtime")
                        stack_append(0)
                    else:
                        stack_append(left % right)
                elif operand == "==":
                    stack_append(left == right)
                elif operand == "!=":
                    stack_append(left != right)
                elif operand == "<":
                    stack_append(left < right)
                elif operand == "<=":
                    stack_append(left <= right)
                elif operand == ">":
                    stack_append(left > right)
                elif operand == ">=":
                    stack_append(left >= right)
                elif operand in ("&&", "and"):
                    stack_append(bool(left) and bool(right))
                elif operand in ("||", "or"):
                    stack_append(bool(left) or bool(right))

            elif op == BytecodeOp.UNARY_OP:
                val = stack_pop() if stack else 0
                if operand == "-":
                    stack_append(-val)
                elif operand == "!":
                    stack_append(not bool(val))

            elif op == BytecodeOp.BUILD_LIST:
                count = int(operand)
                items = []
                for _ in range(count):
                    items.append(stack_pop())
                items.reverse()
                stack_append(items)

            elif op == BytecodeOp.BUILD_DICT:
                count = int(operand)
                pairs = []
                for _ in range(count):
                    v = stack_pop()
                    k = stack_pop()
                    pairs.append((k, v))
                pairs.reverse()
                stack_append(dict(pairs))

            elif op == BytecodeOp.INDEX_GET:
                idx = stack_pop() if stack else 0
                target = stack_pop() if stack else 0
                if isinstance(target, dict):
                    stack_append(target.get(idx, 0))
                elif isinstance(target, (list, str)):
                    try:
                        stack_append(target[int(idx)])
                    except (IndexError, TypeError, ValueError):
                        stack_append(0)
                else:
                    stack_append(0)

            elif op == BytecodeOp.INDEX_SET:
                val = stack_pop() if stack else 0
                idx = stack_pop() if stack else 0
                target = stack_pop() if stack else {}
                if isinstance(target, dict):
                    target[idx] = val
                elif isinstance(target, list):
                    try:
                        int_idx = int(idx)
                        if (int_idx < -len(target) or int_idx >= len(target)) and self.strict_mode:
                            raise IndexError(f"List assignment index {int_idx} out of range (length {len(target)})")
                        target[int_idx] = val
                    except (IndexError, ValueError) as e:
                        if self.strict_mode and isinstance(e, IndexError):
                            raise
                        pass

            elif op == BytecodeOp.JUMP:
                pc = int(operand)

            elif op == BytecodeOp.JUMP_IF_FALSE:
                cond = stack_pop() if stack else False
                if not bool(cond):
                    pc = int(operand)

            elif op == BytecodeOp.CALL_BUILTIN:
                fn_name, argc = operand
                args = []
                for _ in range(argc):
                    args.append(stack_pop())
                args.reverse()

                # If user defined function
                if fn_name in chunk.functions:
                    fn_def = chunk.functions[fn_name]
                    frame = dict(zip(fn_def.params, args))
                    call_stack.append(frame)
                    ret_val = self._execute_instructions(fn_def.code, chunk)
                    call_stack.pop()
                    stack_append(ret_val)
                elif self.dexter_helper._is_builtin(fn_name):
                    res = self.dexter_helper._call_builtin(fn_name, args)
                    stack_append(res)
                else:
                    stack_append(0)

            elif op == BytecodeOp.PRINT:
                val = stack_pop() if stack else ""
                self.stdout.append(str(val))

            elif op == BytecodeOp.POP_TOP:
                if stack:
                    stack_pop()

            elif op == BytecodeOp.RETURN:
                return stack_pop() if stack else 0

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

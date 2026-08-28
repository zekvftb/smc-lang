"""Dexter Virtual Machine (DexterVM) for the SMC Language.

Features:
- Arithmetic expressions, logical comparisons, lists, and first-class dictionaries.
- Standard built-in library: len(), push(), pop(), read_file(), write_file(), str(), int(), type().
- For-in iteration loops and compound assignments (+=, -=, *=, /=).
- Safe negative indexing, division-by-zero guards, and recursion limits.
- Acme-Anvil Time-To-Live (TTL) ephemeral memory.
- Captain Planet content-addressable function dispatch.
- Sailor Moon transformations (MOON_PRISM_POWER) and watchdog fallbacks (TUXEDO_MASK).
- Dee Dee mutation engine for fault-tolerance verification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import random
from typing import Any

from smc.parser import (
    AstNode,
    BinaryOpNode,
    CallRingNode,
    CompoundAssignNode,
    DictNode,
    ExpressionStatementNode,
    FallbackNode,
    ForInNode,
    FunctionCallNode,
    FunctionDefNode,
    HaltNode,
    IfNode,
    IndexAccessNode,
    IndexAssignNode,
    ListNode,
    LiteralNode,
    MutateBlockNode,
    PrintNode,
    ProgramNode,
    ReturnNode,
    SetVarNode,
    SummonNode,
    TransformNode,
    TtlBoxNode,
    UnaryOpNode,
    VariableNode,
    WhileNode,
)


@dataclass
class TtlItem:
    """An ephemeral variable bound with an Acme Anvil countdown timer."""

    value: Any
    ttl: int


class DexterVM:
    """The Dexter Laboratory Virtual Machine execution engine."""

    def __init__(self, seed: int = 42) -> None:
        self.variables: dict[str, Any] = {}
        self.ttl_memory: dict[str, TtlItem] = {}
        self.planeteer_rings: dict[str, list[AstNode]] = {}
        self.functions: dict[str, FunctionDefNode] = {}
        self.call_stack: list[dict[str, Any]] = []
        self.return_triggered: bool = False
        self.last_return_value: Any = None
        self.fallback_handler: list[AstNode] | None = None
        self.stdout: list[str] = []
        self.execution_steps: int = 0
        self.anvils_dropped: int = 0
        self.mutations_survived: int = 0
        self.halted: bool = False
        self.rng = random.Random(seed)

    def _tick_acme_ttls(self) -> None:
        """Tick down all Acme Anvil TTL counters; vaporize expired variables."""
        expired = []
        for name, item in self.ttl_memory.items():
            item.ttl -= 1
            if item.ttl <= 0:
                expired.append(name)

        for name in expired:
            del self.ttl_memory[name]
            self.anvils_dropped += 1
            self.stdout.append(f"[ACME_ANVIL] *ANVIL DROPPED* on '{name}'! Ephemeral variable dissolved.")

    def get_var(self, name: str) -> Any:
        """Resolve a variable from local call stack frame, active Acme TTL memory, or globals."""
        if self.call_stack and name in self.call_stack[-1]:
            return self.call_stack[-1][name]
        if name in self.ttl_memory:
            return self.ttl_memory[name].value
        if name in self.variables:
            return self.variables[name]
        return 0

    def set_var(self, name: str, value: Any) -> None:
        """Set variable in current local frame if within a function, else in global variables."""
        if self.call_stack:
            self.call_stack[-1][name] = value
        else:
            self.variables[name] = value

    # -----------------------------------------------------------------------
    # Built-in Standard Functions
    # -----------------------------------------------------------------------

    def _is_builtin(self, name: str) -> bool:
        return name.lower() in ("len", "push", "pop", "str", "int", "type", "read_file", "write_file")

    def _call_builtin(self, name: str, args: list[Any]) -> Any:
        fn = name.lower()
        if fn == "len":
            target = args[0] if args else []
            return len(target) if hasattr(target, "__len__") else 0

        if fn == "push":
            if args and isinstance(args[0], list):
                val = args[1] if len(args) > 1 else None
                args[0].append(val)
                return args[0]
            return []

        if fn == "pop":
            if args and isinstance(args[0], list) and len(args[0]) > 0:
                return args[0].pop()
            return 0

        if fn == "str":
            return str(args[0]) if args else ""

        if fn == "int":
            try:
                return int(args[0]) if args else 0
            except (ValueError, TypeError):
                return 0

        if fn == "type":
            if not args:
                return "null"
            val = args[0]
            if isinstance(val, dict):
                return "dict"
            if isinstance(val, list):
                return "list"
            if isinstance(val, str):
                return "string"
            if isinstance(val, (int, float)):
                return "number"
            return "object"

        if fn == "read_file":
            if not args:
                return ""
            filepath = Path(str(args[0]))
            try:
                return filepath.read_text(encoding="utf-8")
            except Exception as e:
                self.stdout.append(f"[IO_ERROR] Unable to read '{filepath}': {e}")
                return ""

        if fn == "write_file":
            if len(args) < 2:
                return False
            filepath = Path(str(args[0]))
            content = str(args[1])
            try:
                filepath.parent.mkdir(parents=True, exist_ok=True)
                filepath.write_text(content, encoding="utf-8")
                return True
            except Exception as e:
                self.stdout.append(f"[IO_ERROR] Unable to write '{filepath}': {e}")
                return False

        return 0

    # -----------------------------------------------------------------------
    # Expression Evaluation
    # -----------------------------------------------------------------------

    def evaluate_expression(self, node: AstNode) -> Any:
        """Recursively evaluate an AST expression node."""
        if isinstance(node, LiteralNode):
            return node.value

        if isinstance(node, VariableNode):
            return self.get_var(node.name)

        if isinstance(node, ListNode):
            return [self.evaluate_expression(elem) for elem in node.elements]

        if isinstance(node, DictNode):
            res_dict = {}
            for k_expr, v_expr in node.pairs:
                k = self.evaluate_expression(k_expr)
                v = self.evaluate_expression(v_expr)
                res_dict[k] = v
            return res_dict

        if isinstance(node, IndexAccessNode):
            target = self.evaluate_expression(node.target)
            idx = self.evaluate_expression(node.index_expr)

            # Dictionary key lookup
            if isinstance(target, dict):
                return target.get(idx, 0)

            # List or String indexed access (with safe negative indices)
            if isinstance(target, (list, str)):
                try:
                    int_idx = int(idx)
                    return target[int_idx]
                except (IndexError, TypeError, ValueError):
                    return 0

            return 0

        if isinstance(node, FunctionCallNode):
            evaluated_args = [self.evaluate_expression(arg) for arg in node.args]
            if self._is_builtin(node.name):
                return self._call_builtin(node.name, evaluated_args)
            return self._call_function(node.name, evaluated_args)

        if isinstance(node, UnaryOpNode):
            val = self.evaluate_expression(node.operand)
            if node.op == "-":
                return -val
            if node.op == "!":
                return not bool(val)
            return val

        if isinstance(node, BinaryOpNode):
            left = self.evaluate_expression(node.left)
            right = self.evaluate_expression(node.right)
            op = node.op

            # Arithmetic
            if op == "+":
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                if isinstance(left, list) and isinstance(right, list):
                    return left + right
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if op == "/":
                if right == 0:
                    self.stdout.append("[WARNING] Division by zero detected; clamped to 0.")
                    return 0
                return left / right
            if op == "%":
                return left % right if right != 0 else 0

            # Comparisons
            if op == "==":
                return left == right
            if op == "!=":
                return left != right
            if op == "<":
                return left < right
            if op == "<=":
                return left <= right
            if op == ">":
                return left > right
            if op == ">=":
                return left >= right

        return 0

    def _call_function(self, name: str, arg_values: list[Any]) -> Any:
        """Execute a user-defined function in an isolated local stack frame."""
        if name not in self.functions:
            self.stdout.append(f"[ERROR] Undefined function '{name}' called.")
            return 0

        if len(self.call_stack) >= 100:
            self.stdout.append("[STACK_OVERFLOW] Maximum recursion depth (100 frames) exceeded!")
            return 0

        fn_def = self.functions[name]
        local_frame: dict[str, Any] = {}
        for param, val in zip(fn_def.params, arg_values):
            local_frame[param] = val

        self.call_stack.append(local_frame)
        self.return_triggered = False
        self.last_return_value = 0

        for stmt in fn_def.body:
            if self.halted or self.return_triggered:
                break
            self.execute_node(stmt)

        ret_val = self.last_return_value
        self.return_triggered = False
        self.call_stack.pop()
        return ret_val

    # -----------------------------------------------------------------------
    # Node Execution
    # -----------------------------------------------------------------------

    def execute_node(self, node: AstNode) -> None:
        """Execute a single AST node."""
        if self.halted or self.return_triggered:
            return

        self.execution_steps += 1
        self._tick_acme_ttls()

        # 1. SET_VAR: let x = <expr>
        if isinstance(node, SetVarNode):
            val = self.evaluate_expression(node.expr)
            self.set_var(node.name, val)

        # 2. COMPOUND ASSIGN: x += 1, x -= 5, x *= 2, x /= 2
        elif isinstance(node, CompoundAssignNode):
            curr = self.get_var(node.name)
            operand = self.evaluate_expression(node.expr)
            if node.op == "+=":
                if isinstance(curr, str) or isinstance(operand, str):
                    self.set_var(node.name, str(curr) + str(operand))
                elif isinstance(curr, list) and isinstance(operand, list):
                    self.set_var(node.name, curr + operand)
                else:
                    self.set_var(node.name, curr + operand)
            elif node.op == "-=":
                self.set_var(node.name, curr - operand)
            elif node.op == "*=":
                self.set_var(node.name, curr * operand)
            elif node.op == "/=":
                if operand == 0:
                    self.stdout.append("[WARNING] Division by zero detected; clamped to 0.")
                    self.set_var(node.name, 0)
                else:
                    self.set_var(node.name, curr / operand)

        # 2b. INDEXED ASSIGNMENT: x[key] = val, x[key] -= val
        elif isinstance(node, IndexAssignNode):
            target = self.get_var(node.target_name)
            idx = self.evaluate_expression(node.index_expr)
            new_val = self.evaluate_expression(node.value_expr)
            if isinstance(target, dict):
                curr = target.get(idx, 0)
                if node.op == "=":
                    target[idx] = new_val
                elif node.op == "+=":
                    target[idx] = curr + new_val
                elif node.op == "-=":
                    target[idx] = curr - new_val
                elif node.op == "*=":
                    target[idx] = curr * new_val
                elif node.op == "/=":
                    target[idx] = curr / new_val if new_val != 0 else 0
            elif isinstance(target, list):
                try:
                    int_idx = int(idx)
                    curr = target[int_idx]
                    if node.op == "=":
                        target[int_idx] = new_val
                    elif node.op == "+=":
                        target[int_idx] = curr + new_val
                    elif node.op == "-=":
                        target[int_idx] = curr - new_val
                    elif node.op == "*=":
                        target[int_idx] = curr * new_val
                    elif node.op == "/=":
                        target[int_idx] = curr / new_val if new_val != 0 else 0
                except (IndexError, ValueError):
                    pass

        # 3. TTL_BOX: acme(ttl=N) x = <expr>
        elif isinstance(node, TtlBoxNode):
            val = self.evaluate_expression(node.expr)
            self.ttl_memory[node.name] = TtlItem(value=val, ttl=node.ttl)

        # 4. IF / ELSE
        elif isinstance(node, IfNode):
            cond_val = self.evaluate_expression(node.condition)
            if bool(cond_val):
                for stmt in node.then_branch:
                    if self.halted or self.return_triggered:
                        break
                    self.execute_node(stmt)
            else:
                for stmt in node.else_branch:
                    if self.halted or self.return_triggered:
                        break
                    self.execute_node(stmt)

        # 5. WHILE loop (with max step safety limit)
        elif isinstance(node, WhileNode):
            loop_limit = 5000
            count = 0
            while bool(self.evaluate_expression(node.condition)) and count < loop_limit and not self.halted and not self.return_triggered:
                count += 1
                for stmt in node.body:
                    if self.halted or self.return_triggered:
                        break
                    self.execute_node(stmt)

        # 6. FOR-IN loop: for item in collection { ... }
        elif isinstance(node, ForInNode):
            coll = self.evaluate_expression(node.collection_expr)
            items = []
            if isinstance(coll, dict):
                items = list(coll.keys())
            elif isinstance(coll, (list, str)):
                items = list(coll)

            for item in items:
                if self.halted or self.return_triggered:
                    break
                self.set_var(node.item_name, item)
                for stmt in node.body:
                    if self.halted or self.return_triggered:
                        break
                    self.execute_node(stmt)

        # 7. FUNCTION DEFINITION
        elif isinstance(node, FunctionDefNode):
            self.functions[node.name] = node

        # 8. RETURN
        elif isinstance(node, ReturnNode):
            self.last_return_value = self.evaluate_expression(node.expr)
            self.return_triggered = True

        # 9. EXPRESSION STATEMENT (e.g. standalone func call: push(arr, 1))
        elif isinstance(node, ExpressionStatementNode):
            self.evaluate_expression(node.expr)

        # 10. SUMMON_PLANETEER (Register content-addressable function ring)
        elif isinstance(node, SummonNode):
            self.planeteer_rings[node.ring.upper()] = node.body

        # 11. CALL_RING (Dispatch by Planeteer Ring name)
        elif isinstance(node, CallRingNode):
            ring = node.ring.upper()
            if ring in self.planeteer_rings:
                self.stdout.append(f"[CAPTAIN_PLANET] (Ring: {ring}) Powers combined! Function activated.")
                for stmt in self.planeteer_rings[ring]:
                    if self.halted or self.return_triggered:
                        break
                    self.execute_node(stmt)
            else:
                # Tuxedo Mask Fallback Watchdog
                if self.fallback_handler:
                    self.stdout.append(f"[TUXEDO_MASK] (Watchdog Fallback) Unbound ring '{ring}' intercepted! 'My work here is done.'")
                    for stmt in self.fallback_handler:
                        if self.halted or self.return_triggered:
                            break
                        self.execute_node(stmt)
                else:
                    self.stdout.append(f"[CAPTAIN_PLANET] [WARNING] No matching ring '{ring}' bound in cell.")

        # 12. TRANSFORM (Sailor Moon MOON_PRISM_POWER)
        elif isinstance(node, TransformNode):
            val = self.evaluate_expression(node.expr)
            self.set_var(node.target_var, val)
            self.stdout.append(f"[MOON_PRISM_POWER] (Sailor Moon Transformation) '{node.target_var}' evolved to '{val}'!")
            for stmt in node.body:
                if self.halted or self.return_triggered:
                    break
                self.execute_node(stmt)

        # 13. FALLBACK (Tuxedo Mask registration)
        elif isinstance(node, FallbackNode):
            self.fallback_handler = node.body

        # 14. PRINT
        elif isinstance(node, PrintNode):
            val = self.evaluate_expression(node.expr)
            self.stdout.append(str(val))

        # 15. MUTATE BLOCK ("Dee Dee Mutation")
        elif isinstance(node, MutateBlockNode):
            self.stdout.append("[DEE_DEE] (Mutation Event) 'Oooooh, what does THIS button do?!'")
            self.mutations_survived += 1
            for stmt in node.body:
                if self.halted or self.return_triggered:
                    break
                self.execute_node(stmt)

        # 16. HALT
        elif isinstance(node, HaltNode):
            self.halted = True
            self.stdout.append("[THATS_ALL_FOLKS] [HALT] Program reached clean termination.")

    def run(self, program: ProgramNode) -> dict[str, Any]:
        """Execute complete program AST and return summary execution state."""
        self.stdout.append(f"[DEXTER_VM] [LAB_INIT] Initializing experiment '{program.name}'...")

        for stmt in program.statements:
            if self.halted:
                break
            self.execute_node(stmt)

        return {
            "experiment_name": program.name,
            "execution_steps": self.execution_steps,
            "anvils_dropped": self.anvils_dropped,
            "mutations_survived": self.mutations_survived,
            "stdout": self.stdout,
            "final_variables": dict(self.variables),
            "surviving_ttl_memory": {k: v.value for k, v in self.ttl_memory.items()},
        }

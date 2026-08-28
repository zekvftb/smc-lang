"""Dexter Virtual Machine (DexterVM) for the SMC Language.

Features:
- Arithmetic expressions, logical comparisons, and first-class lists.
- User-defined functions with parameters, local scoping, and return values.
- Control flow: if/else conditionals and while loops.
- Acme-Anvil Time-To-Live (TTL) ephemeral memory.
- Captain Planet content-addressable function dispatch.
- Sailor Moon transformations (MOON_PRISM_POWER) and watchdog fallbacks (TUXEDO_MASK).
- Dee Dee mutation engine for fault-tolerance verification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Any

from smc.parser import (
    AstNode,
    BinaryOpNode,
    CallRingNode,
    ExpressionStatementNode,
    FallbackNode,
    FunctionCallNode,
    FunctionDefNode,
    HaltNode,
    IfNode,
    IndexAccessNode,
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

        if isinstance(node, IndexAccessNode):
            target = self.evaluate_expression(node.target)
            idx = self.evaluate_expression(node.index_expr)
            try:
                return target[int(idx)]
            except (IndexError, TypeError, KeyError):
                return 0

        if isinstance(node, FunctionCallNode):
            return self._call_function(node.name, [self.evaluate_expression(arg) for arg in node.args])

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
                return left / right if right != 0 else 0
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

        # 2. TTL_BOX: acme(ttl=N) x = <expr>
        elif isinstance(node, TtlBoxNode):
            val = self.evaluate_expression(node.expr)
            self.ttl_memory[node.name] = TtlItem(value=val, ttl=node.ttl)

        # 3. IF / ELSE
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

        # 4. WHILE loop (with max step safety limit)
        elif isinstance(node, WhileNode):
            loop_limit = 5000
            count = 0
            while bool(self.evaluate_expression(node.condition)) and count < loop_limit and not self.halted and not self.return_triggered:
                count += 1
                for stmt in node.body:
                    if self.halted or self.return_triggered:
                        break
                    self.execute_node(stmt)

        # 5. FUNCTION DEFINITION
        elif isinstance(node, FunctionDefNode):
            self.functions[node.name] = node

        # 6. RETURN
        elif isinstance(node, ReturnNode):
            self.last_return_value = self.evaluate_expression(node.expr)
            self.return_triggered = True

        # 7. EXPRESSION STATEMENT (e.g. standalone func call)
        elif isinstance(node, ExpressionStatementNode):
            self.evaluate_expression(node.expr)

        # 8. SUMMON_PLANETEER (Register content-addressable function ring)
        elif isinstance(node, SummonNode):
            self.planeteer_rings[node.ring.upper()] = node.body

        # 9. CALL_RING (Dispatch by Planeteer Ring name)
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

        # 10. TRANSFORM (Sailor Moon MOON_PRISM_POWER)
        elif isinstance(node, TransformNode):
            val = self.evaluate_expression(node.expr)
            self.set_var(node.target_var, val)
            self.stdout.append(f"[MOON_PRISM_POWER] (Sailor Moon Transformation) '{node.target_var}' evolved to '{val}'!")
            for stmt in node.body:
                if self.halted or self.return_triggered:
                    break
                self.execute_node(stmt)

        # 11. FALLBACK (Tuxedo Mask registration)
        elif isinstance(node, FallbackNode):
            self.fallback_handler = node.body

        # 12. PRINT
        elif isinstance(node, PrintNode):
            val = self.evaluate_expression(node.expr)
            self.stdout.append(str(val))

        # 13. MUTATE BLOCK ("Dee Dee Mutation")
        elif isinstance(node, MutateBlockNode):
            self.stdout.append("[DEE_DEE] (Mutation Event) 'Oooooh, what does THIS button do?!'")
            self.mutations_survived += 1
            for stmt in node.body:
                if self.halted or self.return_triggered:
                    break
                self.execute_node(stmt)

        # 14. HALT
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

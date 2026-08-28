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
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import importlib
import json
import math
import mimetypes
import os
from pathlib import Path
import random
import sys
import time
from typing import Any

from smc.parser import (
    AstNode,
    AttenuatorNode,
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
    HexaPhaseNode,
    IfNode,
    ImportNode,
    IndexAccessNode,
    IndexAssignNode,
    ListNode,
    LiteralNode,
    MutateBlockNode,
    PrintNode,
    ProgramNode,
    PyImportNode,
    ReturnNode,
    SetVarNode,
    SlipNode,
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
        self.imported_modules: set[Path] = set()
        self.py_modules: dict[str, Any] = {}
        self.current_file: Path | None = None
        self.current_phase_offset: int = 0
        self.rng = random.Random(seed)

    def _marshal_from_python(self, val: Any) -> Any:
        """Recursively marshal Python objects into native SMC representations."""
        if val is None or isinstance(val, (int, float, str, bool)):
            return val
        if isinstance(val, (list, tuple, set)):
            return [self._marshal_from_python(x) for x in val]
        if isinstance(val, dict):
            return {str(k): self._marshal_from_python(v) for k, v in val.items()}
        return str(val)

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
        return name.lower() in (
            "len", "push", "pop", "str", "int", "type", "read_file", "write_file",
            "serve_http", "to_json", "from_json", "range", "split", "join", "keys",
            "values", "contains", "serve_file", "py_call", "py_eval", "py_import",
            "hexaphase_compile", "hexaphase_decompile", "hexaphase_channels", "phase_slip",
            "slip_branch", "g4_latch", "hexaphase_window", "stem_loop_dg", "min", "max"
        )

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
            if isinstance(val, bool):
                return "bool"
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

        if fn == "to_json":
            if not args:
                return "{}"
            try:
                return json.dumps(args[0], indent=2)
            except Exception as e:
                self.stdout.append(f"[JSON_ERROR] Failed to serialize JSON: {e}")
                return "{}"

        if fn == "from_json":
            if not args:
                return {}
            try:
                return json.loads(str(args[0]))
            except Exception as e:
                self.stdout.append(f"[JSON_ERROR] Failed to parse JSON: {e}")
                return {}

        if fn == "range":
            if not args:
                return []
            try:
                if len(args) == 1:
                    return list(range(int(args[0])))
                if len(args) == 2:
                    return list(range(int(args[0]), int(args[1])))
                return list(range(int(args[0]), int(args[1]), int(args[2])))
            except (ValueError, TypeError):
                return []

        if fn == "split":
            if not args:
                return []
            sep = str(args[1]) if len(args) > 1 else None
            return str(args[0]).split(sep)

        if fn == "join":
            if not args:
                return ""
            sep = str(args[1]) if len(args) > 1 else ""
            items = args[0] if isinstance(args[0], list) else []
            return sep.join(str(x) for x in items)

        if fn == "keys":
            if not args or not isinstance(args[0], dict):
                return []
            return list(args[0].keys())

        if fn == "values":
            if not args or not isinstance(args[0], dict):
                return []
            return list(args[0].values())

        if fn == "contains":
            if len(args) < 2:
                return False
            coll, target = args[0], args[1]
            if isinstance(coll, dict):
                return target in coll
            if isinstance(coll, (list, str)):
                return target in coll
            return False

        if fn == "serve_file":
            if not args:
                return {"status": 404, "content_type": "text/html; charset=utf-8", "body": "<h1>404 File Not Specified</h1>"}
            filepath = Path(str(args[0]))
            if filepath.is_file():
                mime, _ = mimetypes.guess_type(str(filepath))
                mime_type = mime or "application/octet-stream"
                try:
                    content = filepath.read_text(encoding="utf-8")
                    return {"status": 200, "content_type": f"{mime_type}; charset=utf-8", "body": content}
                except UnicodeDecodeError:
                    return {"status": 200, "content_type": mime_type, "body": filepath.read_bytes().decode("latin1")}
            return {"status": 404, "content_type": "text/html; charset=utf-8", "body": f"<h1>404 File '{filepath.name}' Not Found</h1>"}

        if fn == "py_call":
            if not args:
                self.stdout.append("[PY_BRIDGE_ERROR] py_call requires a target e.g. 'math.sqrt'.")
                return None
            target_str = str(args[0])
            call_args = list(args[1:])
            try:
                if "." in target_str:
                    parts = target_str.rsplit(".", 1)
                    mod_name, func_name = parts[0], parts[1]
                    if mod_name in self.py_modules:
                        mod = self.py_modules[mod_name]
                    else:
                        mod = importlib.import_module(mod_name)
                    func = getattr(mod, func_name)
                else:
                    func = None
                    for mod in self.py_modules.values():
                        if hasattr(mod, target_str):
                            func = getattr(mod, target_str)
                            break
                    if func is None:
                        import builtins
                        func = getattr(builtins, target_str, None)

                if func is None or not callable(func):
                    self.stdout.append(f"[PY_BRIDGE_ERROR] Could not resolve callable '{target_str}'.")
                    return None

                result = func(*call_args)
                return self._marshal_from_python(result)
            except Exception as e:
                self.stdout.append(f"[PY_BRIDGE_ERROR] Python call '{target_str}' failed: {e}")
                return None

        if fn == "py_eval":
            if not args:
                return None
            expr_str = str(args[0])
            try:
                default_scope = {
                    "math": math,
                    "random": random,
                    "datetime": datetime,
                    "json": json,
                    "time": time,
                    "os": os,
                    "sys": sys,
                }
                scope = dict(default_scope)
                scope.update(self.py_modules)
                scope.update(self.variables)
                result = eval(expr_str, {"__builtins__": __builtins__}, scope)
                return self._marshal_from_python(result)
            except Exception as e:
                self.stdout.append(f"[PY_BRIDGE_ERROR] Python eval '{expr_str}' failed: {e}")
                return None

        if fn == "py_import":
            if not args:
                return None
            mod_name = str(args[0])
            alias = str(args[1]) if len(args) > 1 else mod_name.split(".")[-1]
            try:
                mod = importlib.import_module(mod_name)
                self.py_modules[alias] = mod
                self.stdout.append(f"[PY_BRIDGE] Loaded Python module '{mod_name}' as '{alias}'.")
                return True
            except Exception as e:
                self.stdout.append(f"[PY_BRIDGE_ERROR] Failed to import Python module '{mod_name}': {e}")
                return False

        if fn == "hexaphase_compile":
            if len(args) < 2:
                return ""
            s1, s2 = str(args[0]), str(args[1])
            res = []
            max_l = max(len(s1), len(s2))
            for i in range(max_l):
                if i < len(s1):
                    res.append(s1[i])
                if i < len(s2):
                    res.append(s2[i])
            return "".join(res)

        if fn in ("hexaphase_decompile", "hexaphase_channels"):
            if not args:
                return {}
            s = str(args[0])
            n = len(s)
            return {
                "+0": "".join(s[i] for i in range(0, n, 3)),
                "+1": "".join(s[i] for i in range(1, n, 3)),
                "+2": "".join(s[i] for i in range(2, n, 3)),
                "-0": "".join(s[::-1][i] for i in range(0, n, 3)),
                "-1": "".join(s[::-1][i] for i in range(1, n, 3)),
                "-2": "".join(s[::-1][i] for i in range(2, n, 3)),
            }

        if fn == "phase_slip":
            if not args:
                return ""
            s = str(args[0])
            offset = int(args[1]) if len(args) > 1 else 1
            offset = offset % len(s) if len(s) > 0 else 0
            return s[offset:] + s[:offset]

        if fn == "min":
            if not args:
                return 0
            if len(args) == 1 and isinstance(args[0], (list, tuple)):
                return min(args[0]) if args[0] else 0
            return min(args)

        if fn == "max":
            if not args:
                return 0
            if len(args) == 1 and isinstance(args[0], (list, tuple)):
                return max(args[0]) if args[0] else 0
            return max(args)

        if fn == "slip_branch":
            # slip_branch(prob_pct, val_or_fn_a, val_or_fn_b)
            if not args:
                return None
            prob = float(args[0]) if len(args) > 0 else 50.0
            choice_a = args[1] if len(args) > 1 else True
            choice_b = args[2] if len(args) > 2 else False

            roll = self.rng.uniform(0.0, 100.0)
            chosen = choice_a if roll <= prob else choice_b
            if isinstance(chosen, str) and chosen in self.functions:
                return self._call_function(chosen, [])
            return chosen

        if fn == "g4_latch":
            # g4_latch(current_level, threshold)
            if not args:
                return False
            level = float(args[0])
            thresh = float(args[1]) if len(args) > 1 else 100.0
            is_tripped = level >= thresh
            if is_tripped:
                self.stdout.append(f"[G4_LATCH] Molecular circuit breaker tripped at stress {level:.1f} (Threshold: {thresh:.1f}).")
            return is_tripped

        if fn == "hexaphase_window":
            # hexaphase_window(seq, frame, window_size)
            if not args:
                return []
            s = str(args[0])
            frame = str(args[1]) if len(args) > 1 else "+0"
            w_size = int(args[2]) if len(args) > 2 else 3

            if frame.startswith("-"):
                s = s[::-1]
            offset = 0
            if frame in ("+1", "-1", "1", "-1"):
                offset = 1
            elif frame in ("+2", "-2", "2", "-2"):
                offset = 2

            s_frame = s[offset:]
            return [s_frame[i : i + w_size] for i in range(0, len(s_frame) - w_size + 1, w_size)]

        if fn == "stem_loop_dg":
            # Quick nearest-neighbor dG estimation
            if not args:
                return 0.0
            s = str(args[0]).upper().replace("T", "U")
            gc_count = s.count("G") + s.count("C")
            au_count = s.count("A") + s.count("U")
            return round(-2.5 * gc_count - 1.2 * au_count + 3.5, 2)

        if fn == "serve_http":
            if not args:
                self.stdout.append("[HTTP_SERVER] Error: serve_http requires a port number and handler function name.")
                return False
            port = int(args[0])
            handler_name = str(args[1]) if len(args) > 1 else "handle_request"
            max_requests = int(args[2]) if len(args) > 2 and args[2] is not None else None

            vm_ref = self

            class DexterHTTPHandler(BaseHTTPRequestHandler):
                def do_request(self, method: str):
                    content_len = int(self.headers.get("Content-Length", 0))
                    body_bytes = self.rfile.read(content_len) if content_len > 0 else b""
                    body_str = body_bytes.decode("utf-8", errors="replace")

                    headers_dict = {k: v for k, v in self.headers.items()}
                    req_dict = {
                        "path": self.path,
                        "method": method,
                        "headers": headers_dict,
                        "body": body_str,
                    }

                    # Each request represents an execution cycle in the laboratory
                    vm_ref.execution_steps += 1
                    vm_ref._tick_acme_ttls()

                    response_data = vm_ref._call_function(handler_name, [req_dict])

                    status = 200
                    content_type = "text/html; charset=utf-8"
                    resp_body = ""

                    if isinstance(response_data, dict):
                        status = int(response_data.get("status", 200))
                        content_type = str(response_data.get("content_type", "text/html; charset=utf-8"))
                        resp_body = str(response_data.get("body", ""))
                    elif isinstance(response_data, str):
                        resp_body = response_data
                    else:
                        resp_body = str(response_data)

                    resp_bytes = resp_body.encode("utf-8")

                    self.send_response(status)
                    self.send_header("Content-Type", content_type)
                    self.send_header("Content-Length", str(len(resp_bytes)))
                    self.send_header("Server", "DexterVM-SMC/0.3.0")
                    self.end_headers()
                    self.wfile.write(resp_bytes)

                    log_msg = f"[HTTP_SERVER] {method} {self.path} -> {status} ({len(resp_bytes)} bytes)"
                    vm_ref.stdout.append(log_msg)

                def do_GET(self):
                    self.do_request("GET")

                def do_POST(self):
                    self.do_request("POST")

                def do_PUT(self):
                    self.do_request("PUT")

                def do_DELETE(self):
                    self.do_request("DELETE")

                def log_message(self, format, *args):
                    pass

            server = None
            try:
                server = HTTPServer(("0.0.0.0", port), DexterHTTPHandler)
                self.stdout.append(f"[HTTP_SERVER] Laboratory server listening on http://localhost:{port} (Handler: '{handler_name}')")
                print(f"[DEXTER_VM] Laboratory server online at http://localhost:{port} (Press Ctrl+C to stop)")
                if max_requests is not None:
                    for _ in range(max_requests):
                        server.handle_request()
                else:
                    server.serve_forever()
                return True
            except KeyboardInterrupt:
                self.stdout.append("[HTTP_SERVER] KeyboardInterrupt received; server shutting down cleanly.")
                return True
            except Exception as e:
                self.stdout.append(f"[HTTP_SERVER] Server error: {e}")
                return False
            finally:
                if server:
                    try:
                        server.server_close()
                    except Exception:
                        pass

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

            # Logical
            if op in ("&&", "and"):
                return bool(left) and bool(right)
            if op in ("||", "or"):
                return bool(left) or bool(right)

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

        # 12. TRANSFORM (Sailor Moon MPP - Moon Prism Power)
        elif isinstance(node, TransformNode):
            val = self.evaluate_expression(node.expr)
            self.set_var(node.target_var, val)
            self.stdout.append(f"[MPP] (Sailor Moon Transformation) '{node.target_var}' evolved to '{val}'!")
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

        # 16. IMPORT (Module Loading & Transfection)
        elif isinstance(node, ImportNode):
            mod_path_str = node.path
            base_dir = self.current_file.parent if self.current_file else Path.cwd()
            target_path = (base_dir / mod_path_str).resolve()
            if not target_path.exists() and not mod_path_str.endswith(".smc"):
                target_path = (base_dir / f"{mod_path_str}.smc").resolve()

            if target_path in self.imported_modules:
                return  # Cycle / redundant import guard

            if not target_path.exists():
                self.stdout.append(f"[IMPORT_ERROR] Cannot find module '{mod_path_str}' at '{target_path}'.")
                return

            self.imported_modules.add(target_path)
            try:
                content = target_path.read_text(encoding="utf-8")
                from smc.lexer import SmcLexer
                from smc.parser import SmcParser
                sub_tokens = SmcLexer(content).tokenize()
                sub_ast = SmcParser(sub_tokens, content).parse()
                prev_file = self.current_file
                self.current_file = target_path
                self.run(sub_ast)
                self.current_file = prev_file
                self.stdout.append(f"[IMPORT] Successfully loaded module: {target_path.name}")
            except Exception as e:
                self.stdout.append(f"[IMPORT_ERROR] Failed to execute module '{mod_path_str}': {e}")

        # 17. PY_IMPORT (Python Ecosystem Module Bridge)
        elif isinstance(node, PyImportNode):
            mod_name = node.module_name
            alias = node.alias or mod_name.split(".")[-1]
            try:
                mod = importlib.import_module(mod_name)
                self.py_modules[alias] = mod
                self.stdout.append(f"[PY_BRIDGE] Successfully loaded Python module '{mod_name}' as '{alias}'.")
            except Exception as e:
                self.stdout.append(f"[PY_BRIDGE_ERROR] Failed to import Python module '{mod_name}': {e}")

        # 18. HEXAPHASE (Multiplexed 6-Phase Execution)
        elif isinstance(node, HexaPhaseNode):
            val = self.evaluate_expression(node.target_expr)
            val_str = str(val)
            n = len(val_str)
            phases = {
                "+0": "".join(val_str[i] for i in range(0, n, 3)),
                "+1": "".join(val_str[i] for i in range(1, n, 3)),
                "+2": "".join(val_str[i] for i in range(2, n, 3)),
                "-0": "".join(val_str[::-1][i] for i in range(0, n, 3)),
                "-1": "".join(val_str[::-1][i] for i in range(1, n, 3)),
                "-2": "".join(val_str[::-1][i] for i in range(2, n, 3)),
            }
            self.set_var("hexaphase_channels", phases)
            self.set_var("stream", val_str)
            self.stdout.append(f"[HEXAPHASE] Multiplexed 6-phase channels initialized for stream ({len(val_str)} units).")
            for stmt in node.body:
                if self.halted or self.return_triggered:
                    break
                self.execute_node(stmt)

        # 19. SLIP (Programmed Ribosomal Frameshift)
        elif isinstance(node, SlipNode):
            by_val = int(self.evaluate_expression(node.by_expr))
            self.current_phase_offset = (self.current_phase_offset + by_val) % 3
            self.set_var("current_phase", self.current_phase_offset)
            self.stdout.append(f"[RIBO_SLIP] (Programmed Frameshift) Execution track slipped by {by_val:+d} -> Phase +{self.current_phase_offset}.")

        # 20. ATTENUATOR (Thermodynamic Stem-Loop Pause Gate)
        elif isinstance(node, AttenuatorNode):
            thresh = self.evaluate_expression(node.threshold_expr)
            thresh_num = float(thresh) if isinstance(thresh, (int, float)) else 100.0
            self.stdout.append(f"[ATTENUATOR_GATE] (Stem-Loop Pause Gate) Throttling barrier armed (Threshold: {thresh_num}).")
            for stmt in node.body:
                if self.halted or self.return_triggered:
                    break
                self.execute_node(stmt)

        # 21. HALT
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

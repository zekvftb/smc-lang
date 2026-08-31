"""Interactive Read-Eval-Print Loop (REPL) Shell for SMC Language.

Provides a live, interactive laboratory shell powered by DexterVM.
Maintains persistent session state, supports multi-step calculations,
Acme TTL countdowns, and live function declarations.
"""

from __future__ import annotations

import sys

from smc.lexer import SmcLexer
from smc.parser import SmcParser
from smc.vm import DexterVM


def start_repl() -> None:
    """Launch the interactive SMC REPL session."""
    print("=================================================================")
    print("  DEXTER_VM v1.0.0 (Deterministic EXecution & Transient Runtime)")
    print("  Interactive Language Shell & State Machine")
    print("  Commands: 'exit' to quit, 'clear' to reset, 'vars' to inspect")
    print("=================================================================\n")

    vm = DexterVM()

    while True:
        try:
            line = input("smc> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[DEXTER_VM] Exiting interactive shell.")
            break

        if not line:
            continue

        cmd = line.lower()
        if cmd in ("exit", "quit", "halt", "thats_all_folks"):
            print("[DEXTER_VM] Exiting interactive shell. Goodbye!")
            break

        if cmd == "clear":
            vm = DexterVM()
            print("[DEXTER_VM] Environment cleared. Fresh state initialized.")
            continue

        if cmd == "vars":
            print("--- Persistent Variables ---")
            for k, v in vm.variables.items():
                print(f"  {k} = {v}")
            print("--- Active Acme TTL Memory ---")
            for k, item in vm.ttl_memory.items():
                print(f"  {k} = {item.value} (TTL: {item.ttl} ticks remaining)")
            print("--- Registered Functions ---")
            for f in vm.functions.keys():
                print(f"  fn {f}()")
            print("----------------------------")
            continue

        if cmd == "help":
            print("SMC Quick Reference:")
            print("  let x = 10 + 5            # Declare variable")
            print("  acme(ttl=2) key = 'pass'  # Ephemeral variable")
            print("  fn add(a, b) { return a+b}# Define function")
            print("  let team = ['A', 'B', 'C']# First-class list")
            print("  print x                   # Print to console")
            continue

        try:
            lexer = SmcLexer(line)
            tokens = lexer.tokenize()
            parser = SmcParser(tokens)

            # If user entered a bare expression (e.g. 5 + 10 or team[0]), evaluate and print directly
            ast = parser.parse()
            initial_stdout_len = len(vm.stdout)

            for stmt in ast.statements:
                vm.execute_node(stmt)

            # Print any new stdout messages emitted during execution
            new_stdout = vm.stdout[initial_stdout_len:]
            for out_line in new_stdout:
                # Filter out redundant lab initialization tags in interactive REPL
                if not out_line.startswith("[DEXTER_VM] [LAB_INIT]"):
                    print(out_line)

        except Exception as err:
            print(f"[REPL_ERROR] Error evaluating line: {err}")


if __name__ == "__main__":
    start_repl()

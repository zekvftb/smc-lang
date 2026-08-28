"""Command-Line Interface for SMC (Saturday Morning Cartoons) Language.

Usage:
  smc                      # Launch the interactive live REPL shell
  smc repl                 # Launch the interactive live REPL shell
  smc run <file.smc>       # Execute script in DexterVM
  smc catdog <file.smc>    # Execute CatDog dual-frame interleaved routines
  smc tokens <file.smc>    # Inspect token stream and degenerate opcode mappings
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from smc.lexer import SmcLexer
from smc.parser import CatDogSlicer, SmcParser
from smc.repl import start_repl
from smc.vm import DexterVM


def run_file(file_path: Path | str) -> None:
    path = Path(file_path)
    if not path.is_file():
        print(f"Error: File not found at '{path}'")
        sys.exit(1)

    source = path.read_text(encoding="utf-8")
    lexer = SmcLexer(source)
    tokens = lexer.tokenize()

    parser = SmcParser(tokens)
    ast = parser.parse()

    vm = DexterVM()
    vm.current_file = path.resolve()
    res = vm.run(ast)

    print("\n--- DEXTER_VM EXECUTION OUTPUT ---")
    for line in res["stdout"]:
        print(line)
    print("----------------------------------\n")
    print(f"Steps: {res['execution_steps']} | Anvils Dropped: {res['anvils_dropped']} | Mutations Survived: {res['mutations_survived']}")


def run_catdog(file_path: Path | str) -> None:
    path = Path(file_path)
    if not path.is_file():
        print(f"Error: File not found at '{path}'")
        sys.exit(1)

    source = path.read_text(encoding="utf-8")
    lexer = SmcLexer(source)
    tokens = lexer.tokenize()

    cat_tokens, dog_tokens = CatDogSlicer.slice_frames(tokens)

    print("\n[CAT FRAME] ==================== (OFFSET +0) ====================")
    cat_ast = SmcParser(cat_tokens).parse()
    cat_vm = DexterVM()
    cat_res = cat_vm.run(cat_ast)
    for line in cat_res["stdout"]:
        print(line)

    print("\n[DOG FRAME] ==================== (OFFSET +1) ====================")
    dog_ast = SmcParser(dog_tokens).parse()
    dog_vm = DexterVM()
    dog_res = dog_vm.run(dog_ast)
    for line in dog_res["stdout"]:
        print(line)
    print("===================================================================\n")


def print_tokens(file_path: Path | str) -> None:
    path = Path(file_path)
    if not path.is_file():
        print(f"Error: File not found at '{path}'")
        sys.exit(1)

    source = path.read_text(encoding="utf-8")
    lexer = SmcLexer(source)
    tokens = lexer.tokenize()

    print(f"\n--- TOKEN STREAM FOR {path.name} ---")
    for t in tokens:
        mut_flag = " [MUTATION REPAIRED!]" if t.was_mutated else ""
        op_str = f" -> Opcode.{t.resolved_opcode.value}" if t.resolved_opcode else ""
        print(f"Line {t.line:02d}:{t.column:02d} | {t.token_type.value:<12} | '{t.value}'{op_str}{mut_flag}")
    print("------------------------------------\n")


def main() -> None:
    # If invoked with no arguments, launch REPL directly
    if len(sys.argv) == 1:
        start_repl()
        return

    parser = argparse.ArgumentParser(
        description="SMC (Saturday Morning Cartoons) Language CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # repl command
    subparsers.add_parser("repl", help="Launch interactive live REPL shell")

    # run command
    run_parser = subparsers.add_parser("run", help="Execute an SMC script")
    run_parser.add_argument("file", type=str, help="Path to .smc file")

    # catdog command
    catdog_parser = subparsers.add_parser("catdog", help="Execute dual-frame CatDog interleaved program")
    catdog_parser.add_argument("file", type=str, help="Path to .smc file")

    # tokens command
    tokens_parser = subparsers.add_parser("tokens", help="Inspect tokens and degenerate wobble mappings")
    tokens_parser.add_argument("file", type=str, help="Path to .smc file")

    args = parser.parse_args()

    if args.command == "repl":
        start_repl()
    elif args.command == "run":
        run_file(args.file)
    elif args.command == "catdog":
        run_catdog(args.file)
    elif args.command == "tokens":
        print_tokens(args.file)


if __name__ == "__main__":
    main()

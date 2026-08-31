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

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from smc.lexer import SmcLexer
from smc.parser import CatDogSlicer, SmcParser
from smc.repl import start_repl
from smc.bytecode_vm import BytecodeVM, disassemble_chunk
from smc.compiler import BytecodeCompiler
from smc.vm import DexterVM


def run_file(file_path: Path | str, strict: bool = False, use_ast: bool = False) -> None:
    path = Path(file_path)
    if not path.is_file():
        print(f"Error: File not found at '{path}'")
        sys.exit(1)

    source = path.read_text(encoding="utf-8")
    try:
        lexer = SmcLexer(source, strict=strict)
        tokens = lexer.tokenize()
    except SyntaxError as e:
        print(f"[SYNTAX ERROR] {e}")
        sys.exit(1)

    parser = SmcParser(tokens)
    ast = parser.parse()

    if use_ast:
        # Legacy AST Tree-Walker mode
        vm = DexterVM(strict_mode=strict)
        vm.current_file = path.resolve()
        res = vm.run(ast)

        print("\n--- DEXTER_VM (AST RUNNER) OUTPUT ---")
        for line in res["stdout"]:
            try:
                print(line)
            except UnicodeEncodeError:
                print(line.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8"))
        print("-------------------------------------\n")
        print(f"Steps: {res['execution_steps']} | Anvils Dropped: {res['anvils_dropped']} | Mutations Survived: {res['mutations_survived']}")
    else:
        # Default: High-Speed Linear Bytecode Stack VM
        compiler = BytecodeCompiler()
        chunk = compiler.compile(ast)
        b_vm = BytecodeVM(strict_mode=strict)
        res = b_vm.run(chunk)

        print("\n--- SMC (BYTECODE VM) OUTPUT ---")
        for line in res["stdout"]:
            try:
                print(line)
            except UnicodeEncodeError:
                print(line.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8"))
        print("--------------------------------\n")
        print(f"Instructions Executed: {res['instructions_executed']:,} | Engine: Linear Bytecode Stack VM")


def disassemble_file(file_path: Path | str, strict: bool = False) -> None:
    path = Path(file_path)
    if not path.is_file():
        print(f"Error: File not found at '{path}'")
        sys.exit(1)

    source = path.read_text(encoding="utf-8")
    try:
        lexer = SmcLexer(source, strict=strict)
        tokens = lexer.tokenize()
    except SyntaxError as e:
        print(f"[SYNTAX ERROR] {e}")
        sys.exit(1)

    parser = SmcParser(tokens)
    ast = parser.parse()

    compiler = BytecodeCompiler()
    chunk = compiler.compile(ast)
    dis_str = disassemble_chunk(chunk, f"DISASSEMBLY: {path.name}")
    print("\n" + dis_str + "\n")


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
        try:
            print(line)
        except UnicodeEncodeError:
            print(line.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8"))

    print("\n[DOG FRAME] ==================== (OFFSET +1) ====================")
    dog_ast = SmcParser(dog_tokens).parse()
    dog_vm = DexterVM()
    dog_res = dog_vm.run(dog_ast)
    for line in dog_res["stdout"]:
        try:
            print(line)
        except UnicodeEncodeError:
            print(line.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8"))
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


def init_project(project_name: str, base_path: Path | None = None) -> Path:
    """Scaffold a brand-new SMC laboratory project with modules and web server."""
    base = base_path if base_path is not None else Path.cwd()
    project_dir = base / project_name
    modules_dir = project_dir / "modules"
    public_dir = project_dir / "public"

    project_dir.mkdir(parents=True, exist_ok=True)
    modules_dir.mkdir(parents=True, exist_ok=True)
    public_dir.mkdir(parents=True, exist_ok=True)

    # 1. main.smc
    main_code = (
        '# =============================================================\n'
        f'# SMC Project: {project_name}\n'
        '# =============================================================\n'
        f'experiment "{project_name}"\n\n'
        '# Import external module\n'
        'import "modules/math_utils.smc"\n\n'
        'let server_hits = 0\n\n'
        'fn handle_request(req) {\n'
        '    let p = req["path"]\n'
        '    let m = req["method"]\n'
        '    server_hits += 1\n\n'
        '    print `[HTTP] Incoming ${m} to ${p}`\n\n'
        '    # Static frontend page\n'
        '    if (p == "/") {\n'
        '        return serve_file("public/index.html")\n'
        '    }\n\n'
        '    # Ephemeral session route with Acme TTL\n'
        '    if (p == "/login") {\n'
        '        acme(ttl=5) session_token = "Auth_Secret_12345"\n'
        '        return {\n'
        '            "status": 200,\n'
        '            "content_type": "text/html",\n'
        '            "body": `<h2>Logged in! Session: ${session_token}</h2><p>Auto-expires in 5 hits.</p>`\n'
        '        }\n'
        '    }\n\n'
        '    # JSON API\n'
        '    if (p == "/api/status") {\n'
        '        let radius = 5\n'
        '        let area = circle_area(radius)\n'
        '        return {\n'
        '            "status": 200,\n'
        '            "content_type": "application/json",\n'
        '            "body": to_json({ "status": "ONLINE", "hits": server_hits, "sample_area": area })\n'
        '        }\n'
        '    }\n\n'
        '    return { "status": 404, "body": "404 Not Found" }\n'
        '}\n\n'
        f'print "=== {project_name} Laboratory Online ==="\n'
        'print "Serving HTTP on http://localhost:3000..."\n'
        'serve_http(3000, "handle_request")\n'
    )
    (project_dir / "main.smc").write_text(main_code, encoding="utf-8")

    # 2. modules/math_utils.smc
    mod_code = (
        '# =============================================================\n'
        '# Module: math_utils.smc\n'
        '# =============================================================\n'
        'let PI = 3.14159265\n\n'
        'fn circle_area(r) {\n'
        '    return PI * r * r\n'
        '}\n\n'
        'fn double_val(x) {\n'
        '    return x * 2\n'
        '}\n'
    )
    (modules_dir / "math_utils.smc").write_text(mod_code, encoding="utf-8")

    # 3. public/index.html
    html_code = (
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '    <meta charset="UTF-8">\n'
        f'    <title>{project_name} — Powered by SMC</title>\n'
        '    <style>\n'
        '        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b0f19; color: #f1f5f9; padding: 2rem; }\n'
        '        h1 { color: #00f0ff; }\n'
        '        a { color: #39ff14; text-decoration: none; margin-right: 1.5rem; font-weight: bold; }\n'
        '        .card { background: #161e2e; padding: 2rem; border-radius: 8px; border: 1px solid #263445; max-width: 600px; }\n'
        '    </style>\n'
        '</head>\n'
        '<body>\n'
        '    <div class="card">\n'
        f'        <h1>🧪 {project_name}</h1>\n'
        '        <p>This full-stack application is running 100% on <b>DexterVM</b> in Saturday Morning Cartoons (SMC).</p>\n'
        '        <div style="margin-top: 1.5rem;">\n'
        '            <a href="/login">⚡ Test Acme TTL Login</a>\n'
        '            <a href="/api/status">📊 JSON Status API</a>\n'
        '        </div>\n'
        '    </div>\n'
        '</body>\n'
        '</html>\n'
    )
    (public_dir / "index.html").write_text(html_code, encoding="utf-8")

    # 4. README.md
    readme_code = (
        f'# {project_name}\n\n'
        'A full-stack project built with [SMC (Saturday Morning Cartoons)](https://github.com/zekvftb/smc-lang).\n\n'
        '## 🚀 Getting Started\n\n'
        'Run your application locally:\n\n'
        '```powershell\n'
        'smc run main.smc\n'
        '```\n\n'
        'Then open your browser to **http://localhost:3000**.\n'
    )
    (project_dir / "README.md").write_text(readme_code, encoding="utf-8")

    banner = (
        f"\n[SMC LAB] Project '{project_name}' scaffolded successfully!\n\n"
        f"  Location: {project_dir.resolve()}\n"
        f"  |-- main.smc\n"
        f"  |-- modules/math_utils.smc\n"
        f"  |-- public/index.html\n"
        f"  \\-- README.md\n\n"
        f"To launch your laboratory server:\n"
        f"  cd {project_name}\n"
        f"  smc run main.smc\n"
    )
    print(banner)
    return project_dir


def debug_file(file_path: Path | str) -> None:
    from smc.visualizer import MultiPhaseVisualizer

    path = Path(file_path)
    if not path.is_file():
        print(f"Error: File not found at '{path}'")
        sys.exit(1)

    source = path.read_text(encoding="utf-8")
    tokens = SmcLexer(source).tokenize()
    ast = SmcParser(tokens).parse()

    vm = DexterVM()
    vm.current_file = path.resolve()

    print("\n==================================================================")
    print(f"🐞 SMC Interactive Step Debugger: {path.name}")
    print("Commands: (s)tep | (p)hase | (v)ars | (w)atch <var> | (b)reak <idx> | (c)ont | eval <e> | (q)uit")
    print("==================================================================\n")

    statements = ast.statements
    total_stmts = len(statements)
    idx = 0
    continuous = False
    breakpoints: set[int] = set()
    watchlist: set[str] = set()

    while idx < total_stmts:
        stmt = statements[idx]
        node_name = stmt.__class__.__name__
        step_num = idx + 1

        if continuous and step_num in breakpoints:
            continuous = False
            print(f"\n[DEBUGGER] Hit breakpoint at step {step_num} ({node_name})")

        if not continuous:
            # Display watched variables if any
            if watchlist:
                watched_vals = {k: vm.variables.get(k, "<undefined>") for k in watchlist}
                print(f"  [WATCH] {watched_vals}")

            prompt = f"[{step_num}/{total_stmts}] Phase +{vm.current_phase_offset} | {node_name} > "
            try:
                cmd = input(prompt).strip()
            except (EOFError, KeyboardInterrupt):
                print("\n[DEBUGGER] Aborted.")
                break

            if cmd in ("q", "quit", "exit"):
                print("[DEBUGGER] Exiting.")
                break
            elif cmd in ("v", "vars"):
                print(f"  Active Variables: {vm.variables}")
                continue
            elif cmd in ("p", "phase"):
                print(f"  Phase Diagram: {MultiPhaseVisualizer.render_phase_diagram(vm.current_phase_offset)}")
                continue
            elif cmd.startswith("w ") or cmd.startswith("watch "):
                var_to_watch = cmd.split(None, 1)[1].strip()
                watchlist.add(var_to_watch)
                print(f"  [WATCHLIST] Now watching '{var_to_watch}'")
                continue
            elif cmd.startswith("b ") or cmd.startswith("break "):
                try:
                    bp_val = int(cmd.split(None, 1)[1].strip())
                    breakpoints.add(bp_val)
                    print(f"  [BREAKPOINT] Added breakpoint at step {bp_val}")
                except ValueError:
                    print("  [ERROR] Invalid step number for breakpoint.")
                continue
            elif cmd.startswith("eval "):
                expr_src = cmd[5:].strip()
                try:
                    expr_tokens = SmcLexer(expr_src).tokenize()
                    expr_node = SmcParser(expr_tokens).parse_expression()
                    res = vm.evaluate_expression(expr_node)
                    print(f"  => {res}")
                except Exception as e:
                    print(f"  [EVAL ERROR] {e}")
                continue
            elif cmd in ("c", "cont", "continue"):
                continuous = True

        # Execute statement
        vm.execute_node(stmt)
        if vm.stdout:
            while vm.stdout:
                line = vm.stdout.pop(0)
                print(f"  [OUT] {line}")
        idx += 1

    print("\n==================================================================")
    print(f"✅ Debugger finished. Final Variables: {vm.variables}")
    print("==================================================================\n")


def main() -> None:
    # If invoked with no arguments, launch REPL directly
    if len(sys.argv) == 1:
        start_repl()
        return

    parser = argparse.ArgumentParser(
        prog="smc",
        description="SMC (Saturday Morning Cartoons) Language CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-V", "--version", action="version", version="smc 1.0.0")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # repl command
    subparsers.add_parser("repl", help="Launch interactive live REPL shell")

    # init command
    init_parser = subparsers.add_parser("init", help="Scaffold a new modular SMC project")
    init_parser.add_argument("name", type=str, nargs="?", default="my_smc_app", help="Name of project to create")

    # run command
    run_parser = subparsers.add_parser("run", help="Execute an SMC script (default: fast Bytecode VM)")
    run_parser.add_argument("file", type=str, help="Path to .smc file")
    run_parser.add_argument("--strict", action="store_true", help="Enforce exact keyword matching with zero fuzzy repairs")
    run_parser.add_argument("--ast", action="store_true", help="Use legacy AST tree-walker instead of default Bytecode VM")

    # dis command (disassemble bytecode)
    dis_parser = subparsers.add_parser("dis", help="Disassemble an SMC script into linear VM bytecode")
    dis_parser.add_argument("file", type=str, help="Path to .smc file")
    dis_parser.add_argument("--strict", action="store_true", help="Enforce exact keyword matching")

    # debug command
    debug_parser = subparsers.add_parser("debug", help="Step-debug an SMC script interactively")
    debug_parser.add_argument("file", type=str, help="Path to .smc file")

    # catdog command
    catdog_parser = subparsers.add_parser("catdog", help="Execute dual-frame CatDog interleaved program")
    catdog_parser.add_argument("file", type=str, help="Path to .smc file")

    # tokens command
    tokens_parser = subparsers.add_parser("tokens", help="Inspect tokens and degenerate wobble mappings")
    tokens_parser.add_argument("file", type=str, help="Path to .smc file")

    args = parser.parse_args()

    if args.command == "repl":
        start_repl()
    elif args.command == "init":
        init_project(args.name)
    elif args.command == "run":
        run_file(args.file, strict=args.strict, use_ast=args.ast)
    elif args.command == "dis":
        disassemble_file(args.file, strict=args.strict)
    elif args.command == "debug":
        debug_file(args.file)
    elif args.command == "catdog":
        run_catdog(args.file)
    elif args.command == "tokens":
        print_tokens(args.file)


if __name__ == "__main__":
    main()

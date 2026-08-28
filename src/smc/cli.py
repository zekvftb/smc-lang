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
        try:
            print(line)
        except UnicodeEncodeError:
            print(line.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8"))
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

    # init command
    init_parser = subparsers.add_parser("init", help="Scaffold a new modular SMC project")
    init_parser.add_argument("name", type=str, nargs="?", default="my_smc_app", help="Name of project to create")

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
    elif args.command == "init":
        init_project(args.name)
    elif args.command == "run":
        run_file(args.file)
    elif args.command == "catdog":
        run_catdog(args.file)
    elif args.command == "tokens":
        print_tokens(args.file)


if __name__ == "__main__":
    main()

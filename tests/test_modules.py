"""Automated unit tests for SMC modular multi-file import system."""

from pathlib import Path
import pytest

from smc.lexer import SmcLexer
from smc.parser import SmcParser
from smc.vm import DexterVM


def test_basic_module_import(tmp_path: Path):
    """Verify importing a helper module loads its functions and variables."""
    helper_file = tmp_path / "math_helper.smc"
    helper_file.write_text(
        "let PI = 3.14159\n"
        "fn square(x) {\n"
        "    return x * x\n"
        "}\n",
        encoding="utf-8"
    )

    main_code = (
        f"import '{helper_file.name}'\n"
        "let area = square(4)\n"
        "halt\n"
    )

    tokens = SmcLexer(main_code).tokenize()
    ast = SmcParser(tokens).parse()
    vm = DexterVM()
    vm.current_file = tmp_path / "main.smc"
    res = vm.run(ast)

    vars = res["final_variables"]
    assert vars["PI"] == 3.14159
    assert vars["area"] == 16
    assert any("Successfully loaded module: math_helper.smc" in line for line in res["stdout"])


def test_nested_module_imports(tmp_path: Path):
    """Verify A imports B, and Main imports A."""
    mod_b = tmp_path / "mod_b.smc"
    mod_b.write_text("let b_val = 100\n", encoding="utf-8")

    mod_a = tmp_path / "mod_a.smc"
    mod_a.write_text(
        "import 'mod_b.smc'\n"
        "let a_val = b_val * 2\n",
        encoding="utf-8"
    )

    main_code = (
        "import 'mod_a.smc'\n"
        "let final_sum = a_val + b_val\n"
        "halt\n"
    )

    tokens = SmcLexer(main_code).tokenize()
    ast = SmcParser(tokens).parse()
    vm = DexterVM()
    vm.current_file = tmp_path / "main.smc"
    res = vm.run(ast)

    vars = res["final_variables"]
    assert vars["b_val"] == 100
    assert vars["a_val"] == 200
    assert vars["final_sum"] == 300


def test_cyclic_import_guard(tmp_path: Path):
    """Verify cyclic imports (a -> b -> a) do not trigger an infinite loop."""
    mod_one = tmp_path / "one.smc"
    mod_two = tmp_path / "two.smc"

    mod_one.write_text("import 'two.smc'\nlet one_loaded = true\n", encoding="utf-8")
    mod_two.write_text("import 'one.smc'\nlet two_loaded = true\n", encoding="utf-8")

    main_code = "import 'one.smc'\nhalt\n"

    tokens = SmcLexer(main_code).tokenize()
    ast = SmcParser(tokens).parse()
    vm = DexterVM()
    vm.current_file = tmp_path / "main.smc"
    res = vm.run(ast)

    vars = res["final_variables"]
    assert vars["one_loaded"] is True
    assert vars["two_loaded"] is True


def test_missing_module_error(tmp_path: Path):
    """Verify importing a nonexistent module outputs an error without crashing the process."""
    main_code = "import 'ghost_module.smc'\nlet alive = true\nhalt\n"
    tokens = SmcLexer(main_code).tokenize()
    ast = SmcParser(tokens).parse()
    vm = DexterVM()
    vm.current_file = tmp_path / "main.smc"
    res = vm.run(ast)

    assert any("[IMPORT_ERROR]" in line for line in res["stdout"])
    assert res["final_variables"]["alive"] is True

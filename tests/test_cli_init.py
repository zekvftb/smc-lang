"""Automated tests for SMC project scaffolding CLI ('smc init')."""

from pathlib import Path
import pytest

from smc.cli import init_project
from smc.lexer import SmcLexer
from smc.parser import SmcParser
from smc.vm import DexterVM


def test_init_project_scaffolding(tmp_path: Path):
    """Verify that init_project generates a complete, valid SMC project structure."""
    proj_dir = init_project("galaxy_lab", base_path=tmp_path)

    assert proj_dir.is_dir()
    assert (proj_dir / "main.smc").is_file()
    assert (proj_dir / "modules" / "math_utils.smc").is_file()
    assert (proj_dir / "public" / "index.html").is_file()
    assert (proj_dir / "README.md").is_file()

    # Verify that the generated module works
    mod_code = (proj_dir / "modules" / "math_utils.smc").read_text(encoding="utf-8")
    mod_tokens = SmcLexer(mod_code).tokenize()
    mod_ast = SmcParser(mod_tokens).parse()

    vm = DexterVM()
    vm.run(mod_ast)
    assert "PI" in vm.variables
    assert "circle_area" in vm.functions
    assert vm._call_function("circle_area", [4]) == 3.14159265 * 16

    # Verify that main.smc parses cleanly
    main_code = (proj_dir / "main.smc").read_text(encoding="utf-8")
    main_tokens = SmcLexer(main_code).tokenize()
    main_ast = SmcParser(main_tokens).parse()
    assert main_ast is not None

"""Unit tests for Stage 4: Dictionaries, For-In Loops, Built-ins, Compound Assign, and Safety Guards."""

from pathlib import Path
import pytest

from smc.lexer import SmcLexer
from smc.parser import SmcParser
from smc.vm import DexterVM


def run_code(code: str) -> dict:
    tokens = SmcLexer(code).tokenize()
    ast = SmcParser(tokens).parse()
    vm = DexterVM()
    return vm.run(ast)


def test_first_class_dictionaries():
    """Verify dictionary literals and key-value lookups."""
    code = (
        "let hero = {'name': 'Sailor_Mars', 'hp': 100, 'element': 'FIRE'}\n"
        "let hero_name = hero['name']\n"
        "let hero_hp = hero['hp']\n"
        "halt\n"
    )
    res = run_code(code)
    vars = res["final_variables"]
    assert vars["hero_name"] == "Sailor_Mars"
    assert vars["hero_hp"] == 100


def test_for_in_loop():
    """Verify for-in loop iterates over collection elements cleanly."""
    code = (
        "let team = ['Blossom', 'Bubbles', 'Buttercup']\n"
        "let collected = []\n"
        "for hero in team {\n"
        "    push(collected, hero)\n"
        "}\n"
        "let count = len(collected)\n"
        "halt\n"
    )
    res = run_code(code)
    vars = res["final_variables"]
    assert vars["collected"] == ["Blossom", "Bubbles", "Buttercup"]
    assert vars["count"] == 3


def test_compound_assignments():
    """Verify +=, -=, *= compound operators."""
    code = (
        "let score = 100\n"
        "score += 25\n"      # 125
        "score -= 5\n"       # 120
        "score *= 2\n"       # 240
        "halt\n"
    )
    res = run_code(code)
    assert res["final_variables"]["score"] == 240


def test_indexed_assignment():
    """Verify indexed assignment on dictionaries and lists."""
    code = (
        "let hero = {'hp': 100}\n"
        "hero['hp'] -= 20\n"
        "hero['mana'] = 50\n"
        "let team = ['Blossom', 'Bubbles']\n"
        "team[0] = 'Commander_Blossom'\n"
        "halt\n"
    )
    res = run_code(code)
    vars = res["final_variables"]
    assert vars["hero"]["hp"] == 80
    assert vars["hero"]["mana"] == 50
    assert vars["team"][0] == "Commander_Blossom"


def test_builtin_functions():
    """Verify standard library built-in functions: len, push, pop, str, int, type."""
    code = (
        "let items = ['alpha', 'beta']\n"
        "let initial_len = len(items)\n"
        "push(items, 'gamma')\n"
        "let after_push_len = len(items)\n"
        "let popped = pop(items)\n"
        "let num_str = str(42)\n"
        "let parsed_int = int('999')\n"
        "let dict_type = type({'k': 1})\n"
        "halt\n"
    )
    res = run_code(code)
    vars = res["final_variables"]
    assert vars["initial_len"] == 2
    assert vars["after_push_len"] == 3
    assert vars["popped"] == "gamma"
    assert vars["num_str"] == "42"
    assert vars["parsed_int"] == 999
    assert vars["dict_type"] == "dict"


def test_safe_negative_indexing():
    """Verify negative indexing works for lists and strings."""
    code = (
        "let list_items = ['first', 'middle', 'last']\n"
        "let last_elem = list_items[-1]\n"
        "let second_last = list_items[-2]\n"
        "halt\n"
    )
    res = run_code(code)
    vars = res["final_variables"]
    assert vars["last_elem"] == "last"
    assert vars["second_last"] == "middle"


def test_division_by_zero_guard():
    """Verify division by zero produces safe warning without crashing VM."""
    code = (
        "let safe_res = 50 / 0\n"
        "halt\n"
    )
    res = run_code(code)
    assert res["final_variables"]["safe_res"] == 0
    assert any("Division by zero detected" in line for line in res["stdout"])


def test_recursion_depth_limit():
    """Verify runaway recursion is safely intercepted at 500 frames."""
    code = (
        "fn infinite_loop(n) {\n"
        "    return infinite_loop(n + 1)\n"
        "}\n"
        "let res = infinite_loop(1)\n"
        "halt\n"
    )
    res = run_code(code)
    assert any("Maximum recursion depth" in line for line in res["stdout"])


def test_file_io(tmp_path: Path):
    """Verify read_file and write_file built-ins."""
    test_file = str(tmp_path / "smc_io_test.txt").replace("\\", "/")
    code = (
        f"let ok = write_file('{test_file}', 'Chemical X Laboratory Data')\n"
        f"let content = read_file('{test_file}')\n"
        "halt\n"
    )
    res = run_code(code)
    vars = res["final_variables"]
    assert vars["ok"] is True
    assert vars["content"] == "Chemical X Laboratory Data"

"""Automated tests for SMC v0.4.0 'Developer Joy' Quality of Life Features:
- Template strings (`${var}`)
- Native JSON serialization & parsing (to_json, from_json)
- First-class booleans (true, false, null) & logical operators (&&, ||, and, or)
- range() loops
- Collection utilities (split, join, keys, values, contains)
- serve_file() static asset delivery
"""

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


def test_template_string_interpolation():
    """Verify backtick template strings interpolate variables and expressions."""
    code = (
        "let hero = 'Blossom'\n"
        "let power = 50\n"
        "let msg = `Hero: ${hero} | Total Power: ${power * 2}!`\n"
        "halt\n"
    )
    res = run_code(code)
    assert res["final_variables"]["msg"] == "Hero: Blossom | Total Power: 100!"


def test_native_json_builtins():
    """Verify to_json and from_json serialize and deserialize complex structures."""
    code = (
        "let original = {'app': 'DexterLab', 'version': 4, 'active': true, 'tags': ['science', 'toons']}\n"
        "let serialized = to_json(original)\n"
        "let deserialized = from_json(serialized)\n"
        "let app_name = deserialized['app']\n"
        "let ver = deserialized['version']\n"
        "halt\n"
    )
    res = run_code(code)
    vars = res["final_variables"]
    assert vars["app_name"] == "DexterLab"
    assert vars["ver"] == 4
    assert vars["deserialized"]["active"] is True
    assert vars["deserialized"]["tags"] == ["science", "toons"]


def test_booleans_and_logical_operators():
    """Verify true, false, null literals and &&, ||, and, or operations."""
    code = (
        "let t = true\n"
        "let f = false\n"
        "let n = null\n"
        "let c_and = true && false\n"
        "let c_or = true || false\n"
        "let c_word_and = (10 > 5) and (20 > 10)\n"
        "let c_word_or = (5 > 100) or (1 == 1)\n"
        "halt\n"
    )
    res = run_code(code)
    vars = res["final_variables"]
    assert vars["t"] is True
    assert vars["f"] is False
    assert vars["n"] is None
    assert vars["c_and"] is False
    assert vars["c_or"] is True
    assert vars["c_word_and"] is True
    assert vars["c_word_or"] is True


def test_range_in_for_loops():
    """Verify range() generates clean sequence loops."""
    code = (
        "let total = 0\n"
        "let nums = []\n"
        "for i in range(1, 6) {\n"
        "    total += i\n"
        "    push(nums, i)\n"
        "}\n"
        "halt\n"
    )
    res = run_code(code)
    vars = res["final_variables"]
    assert vars["total"] == 15  # 1+2+3+4+5
    assert vars["nums"] == [1, 2, 3, 4, 5]


def test_collection_toolkit():
    """Verify split, join, keys, values, and contains."""
    code = (
        "let csv = 'Mercury,Mars,Jupiter'\n"
        "let planets = split(csv, ',')\n"
        "let joined = join(planets, ' - ')\n"
        "let hero_stats = {'hp': 100, 'mana': 50}\n"
        "let stat_keys = keys(hero_stats)\n"
        "let stat_vals = values(hero_stats)\n"
        "let has_hp = contains(hero_stats, 'hp')\n"
        "let has_speed = contains(hero_stats, 'speed')\n"
        "let has_mars = contains(planets, 'Mars')\n"
        "let has_pluto = contains(planets, 'Pluto')\n"
        "halt\n"
    )
    res = run_code(code)
    vars = res["final_variables"]
    assert vars["planets"] == ["Mercury", "Mars", "Jupiter"]
    assert vars["joined"] == "Mercury - Mars - Jupiter"
    assert set(vars["stat_keys"]) == {"hp", "mana"}
    assert set(vars["stat_vals"]) == {100, 50}
    assert vars["has_hp"] is True
    assert vars["has_speed"] is False
    assert vars["has_mars"] is True
    assert vars["has_pluto"] is False


def test_serve_file_helper(tmp_path: Path):
    """Verify serve_file detects mime type and returns structured response."""
    test_css = tmp_path / "style.css"
    test_css.write_text("body { background: black; }", encoding="utf-8")

    css_path = str(test_css).replace("\\", "/")
    code = (
        f"let res_ok = serve_file('{css_path}')\n"
        "let res_404 = serve_file('nonexistent_asset.css')\n"
        "halt\n"
    )
    res = run_code(code)
    vars = res["final_variables"]
    assert vars["res_ok"]["status"] == 200
    assert "text/css" in vars["res_ok"]["content_type"]
    assert vars["res_ok"]["body"] == "body { background: black; }"

    assert vars["res_404"]["status"] == 404

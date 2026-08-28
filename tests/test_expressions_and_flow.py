"""Unit tests for Stage 2: Expressions, Control Flow, and Sailor Moon features."""

import pytest

from smc.lexer import SmcLexer
from smc.parser import SmcParser
from smc.vm import DexterVM


def run_code(code: str) -> dict:
    tokens = SmcLexer(code).tokenize()
    ast = SmcParser(tokens).parse()
    vm = DexterVM()
    return vm.run(ast)


def test_math_operator_precedence():
    """Verify arithmetic follows standard order of operations (* and / before + and -)."""
    code = (
        "let result1 = 2 + 3 * 4\n"       # 2 + 12 = 14
        "let result2 = (2 + 3) * 4\n"     # 5 * 4 = 20
        "let result3 = 100 - 50 / 2\n"    # 100 - 25 = 75
        "let result4 = 17 % 5\n"          # 2
        "print result1\n"
        "print result2\n"
        "halt\n"
    )
    res = run_code(code)
    vars = res["final_variables"]
    assert vars["result1"] == 14
    assert vars["result2"] == 20
    assert vars["result3"] == 75
    assert vars["result4"] == 2


def test_if_else_conditionals():
    """Verify conditional branching based on comparisons."""
    code = (
        "let power = 9001\n"
        "if (power > 9000) {\n"
        "    let status = 'OverNineThousand'\n"
        "} else {\n"
        "    let status = 'Normal'\n"
        "}\n"
        "halt\n"
    )
    res = run_code(code)
    assert res["final_variables"]["status"] == "OverNineThousand"


def test_while_loop_iteration():
    """Verify while loops execute iteratively until condition becomes false."""
    code = (
        "let count = 0\n"
        "let total = 0\n"
        "while (count < 5) {\n"
        "    let count = count + 1\n"
        "    let total = total + count\n"
        "}\n"
        "halt\n"
    )
    res = run_code(code)
    # count: 5, total: 1 + 2 + 3 + 4 + 5 = 15
    assert res["final_variables"]["count"] == 5
    assert res["final_variables"]["total"] == 15


def test_sailor_moon_transformation():
    """Verify MOON_PRISM_POWER state transformation."""
    code = (
        "let civilian = 'Usagi_Tsukino'\n"
        "MOON_PRISM_POWER civilian = 'Sailor_Moon' {\n"
        "    print 'In the name of the Moon, I will punish you!'\n"
        "}\n"
        "halt\n"
    )
    res = run_code(code)
    assert res["final_variables"]["civilian"] == "Sailor_Moon"
    assert any("Sailor Moon Transformation" in s for s in res["stdout"])
    assert any("In the name of the Moon" in s for s in res["stdout"])


def test_tuxedo_mask_watchdog_fallback():
    """Verify Tuxedo Mask intervenes when an unbound ring is dispatched."""
    code = (
        "TUXEDO_MASK {\n"
        "    print 'Rose thrown: Target shielded!'\n"
        "}\n"
        "# Dispatch a ring that was never bound\n"
        "dispatch 'NEPTUNE'\n"
        "halt\n"
    )
    res = run_code(code)
    assert any("Watchdog Fallback" in s for s in res["stdout"])
    assert any("Rose thrown: Target shielded!" in s for s in res["stdout"])

"""Unit tests for DexterVM execution, Acme TTL, and Captain Planet dispatch."""

import pytest

from smc.lexer import SmcLexer
from smc.parser import SmcParser
from smc.vm import DexterVM


def test_dexter_vm_basic_execution():
    """Verify basic assignment and output."""
    code = (
        "SUGAR candy = 42\n"
        "KAMEHAMEHA candy\n"
        "THATS_ALL_FOLKS\n"
    )
    tokens = SmcLexer(code).tokenize()
    ast = SmcParser(tokens).parse()
    vm = DexterVM()
    res = vm.run(ast)

    assert res["final_variables"]["candy"] == 42
    assert "42" in res["stdout"]


def test_acme_anvil_ttl_expiration():
    """Verify Acme Anvil TTL auto-vaporizes variables without garbage collection."""
    # Variable secret has TTL of 2 steps
    code = (
        "ACME_ANVIL_BOX(ttl=2) secret = 'TopSecret'\n"
        "KAMEHAMEHA 'Step1'\n"
        "KAMEHAMEHA 'Step2'\n"
        "KAMEHAMEHA 'Step3'\n"
        "THATS_ALL_FOLKS\n"
    )
    tokens = SmcLexer(code).tokenize()
    ast = SmcParser(tokens).parse()
    vm = DexterVM()
    res = vm.run(ast)

    # Anvil must have dropped!
    assert res["anvils_dropped"] >= 1
    # Variable must be dissolved from active TTL memory
    assert "secret" not in res["surviving_ttl_memory"]
    assert any("[ACME_ANVIL] *ANVIL DROPPED* on 'secret'" in s for s in res["stdout"])


def test_captain_planet_content_addressable_dispatch():
    """Verify shape-based function binding and execution."""
    code = (
        "SUMMON_PLANETEER(ring='FIRE') {\n"
        "    KAMEHAMEHA 'Wheeler Fire Blast!'\n"
        "}\n"
        "POWERS_COMBINED 'FIRE'\n"
        "THATS_ALL_FOLKS\n"
    )
    tokens = SmcLexer(code).tokenize()
    ast = SmcParser(tokens).parse()
    vm = DexterVM()
    res = vm.run(ast)

    assert any("Wheeler Fire Blast!" in s for s in res["stdout"])
    assert any("(Ring: FIRE)" in s for s in res["stdout"])

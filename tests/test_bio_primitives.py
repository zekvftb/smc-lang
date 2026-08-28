"""Unit tests for SMC bio-hardware state primitives and built-ins."""

import pytest
from smc.lexer import SmcLexer
from smc.parser import SmcParser
from smc.vm import DexterVM


def run_code(code: str) -> DexterVM:
    tokens = SmcLexer(code).tokenize()
    ast = SmcParser(tokens).parse()
    vm = DexterVM()
    vm.run(ast)
    return vm


def test_smc_min_max_builtins():
    code = """
    var a = min(10, 25, 3)
    var b = max(10, 25, 3)
    var list_min = min([50, 12, 88])
    var list_max = max([50, 12, 88])
    """
    vm = run_code(code)
    assert vm.get_var("a") == 3
    assert vm.get_var("b") == 25
    assert vm.get_var("list_min") == 12
    assert vm.get_var("list_max") == 88


def test_smc_slip_branch_probabilistic():
    code = """
    func on_slipped() {
        return "SLIPPED_FRAME"
    }
    func on_straight() {
        return "MAINTAINED_FRAME"
    }
    var always_slipped = slip_branch(100.0, "on_slipped", "on_straight")
    var never_slipped = slip_branch(0.0, "on_slipped", "on_straight")
    var direct_val = slip_branch(100.0, 42, 99)
    """
    vm = run_code(code)
    assert vm.get_var("always_slipped") == "SLIPPED_FRAME"
    assert vm.get_var("never_slipped") == "MAINTAINED_FRAME"
    assert vm.get_var("direct_val") == 42


def test_smc_g4_latch_circuit_breaker():
    code = """
    var low_stress = g4_latch(50, 100)
    var high_stress = g4_latch(120, 100)
    """
    vm = run_code(code)
    assert vm.get_var("low_stress") is False
    assert vm.get_var("high_stress") is True
    assert any("[G4_LATCH]" in line for line in vm.stdout)


def test_smc_hexaphase_window_extractor():
    code = """
    var seq = "ATGCGATCGTAA"
    var frame0_codons = hexaphase_window(seq, "+0", 3)
    var frame1_codons = hexaphase_window(seq, "+1", 3)
    """
    vm = run_code(code)
    f0 = vm.get_var("frame0_codons")
    f1 = vm.get_var("frame1_codons")
    assert f0 == ["ATG", "CGA", "TCG", "TAA"]
    assert f1 == ["TGC", "GAT", "CGT"]


def test_smc_stem_loop_dg():
    code = """
    var stable_hairpin = "GCGCGC"
    var weak_hairpin = "AAAAAA"
    var dG_stable = stem_loop_dg(stable_hairpin)
    var dG_weak = stem_loop_dg(weak_hairpin)
    """
    vm = run_code(code)
    assert vm.get_var("dG_stable") < vm.get_var("dG_weak")

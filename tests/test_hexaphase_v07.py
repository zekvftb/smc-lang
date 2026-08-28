"""Unit tests for SMC v0.7.0 HexaPhase Architecture & Biological Execution Gates."""

import pytest
from smc.lexer import SmcLexer
from smc.parser import HexaPhaseSlicer, SmcParser
from smc.vm import DexterVM


def test_hexaphase_slicer_6_phases():
    """Verify HexaPhaseSlicer extracts all 6 forward and reverse reading phases."""
    code = "let a = 1 let b = 2 let c = 3"
    tokens = SmcLexer(code).tokenize()
    phases = HexaPhaseSlicer.slice_phases(tokens)

    assert "+0" in phases
    assert "+1" in phases
    assert "+2" in phases
    assert "-0" in phases
    assert "-1" in phases
    assert "-2" in phases
    assert len(phases["+0"]) > 0


def test_hexaphase_block_execution():
    """Verify hexaphase block decomposes stream into 6 accessible channels."""
    code = """
    experiment "HexaPhase_Test"
    hexaphase "ABCDEF" {
        let p0 = hexaphase_channels["+0"]
        let p1 = hexaphase_channels["+1"]
        let p2 = hexaphase_channels["+2"]
    }
    halt
    """
    tokens = SmcLexer(code).tokenize()
    ast = SmcParser(tokens, code).parse()
    vm = DexterVM()
    res = vm.run(ast)

    assert res["final_variables"]["p0"] == "AD"
    assert res["final_variables"]["p1"] == "BE"
    assert res["final_variables"]["p2"] == "CF"
    assert any("[HEXAPHASE]" in line for line in res["stdout"])


def test_slip_programmed_ribosomal_frameshifting():
    """Verify slip(+1) modifies current_phase offset."""
    code = """
    experiment "PRF_Test"
    slip(1)
    let p_after1 = current_phase
    slip(1)
    let p_after2 = current_phase
    slip(1)
    let p_after3 = current_phase
    halt
    """
    tokens = SmcLexer(code).tokenize()
    ast = SmcParser(tokens, code).parse()
    vm = DexterVM()
    res = vm.run(ast)

    assert res["final_variables"]["p_after1"] == 1
    assert res["final_variables"]["p_after2"] == 2
    assert res["final_variables"]["p_after3"] == 0  # Wraps modulo 3
    assert any("[RIBO_SLIP]" in line for line in res["stdout"])


def test_attenuator_gate_execution():
    """Verify attenuator gate armed and executes body statements."""
    code = """
    experiment "Attenuator_Test"
    attenuator(delta_g = -14.5) {
        let gate_status = "ARMED"
    }
    halt
    """
    tokens = SmcLexer(code).tokenize()
    ast = SmcParser(tokens, code).parse()
    vm = DexterVM()
    res = vm.run(ast)

    assert res["final_variables"]["gate_status"] == "ARMED"
    assert any("[ATTENUATOR_GATE]" in line for line in res["stdout"])


def test_hexaphase_builtins():
    """Verify hexaphase_compile, hexaphase_channels, and phase_slip built-ins."""
    code = """
    experiment "HexaPhase_Builtins_Test"
    let compiled = hexaphase_compile("ACE", "BDF")
    let channels = hexaphase_channels(compiled)
    let slipped = phase_slip("ABCDEF", 2)
    halt
    """
    tokens = SmcLexer(code).tokenize()
    ast = SmcParser(tokens, code).parse()
    vm = DexterVM()
    res = vm.run(ast)

    assert res["final_variables"]["compiled"] == "ABCDEF"
    assert res["final_variables"]["channels"]["+0"] == "AD"
    assert res["final_variables"]["slipped"] == "CDEFAB"

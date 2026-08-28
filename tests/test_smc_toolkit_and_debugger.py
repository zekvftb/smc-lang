"""Unit tests for SMC Data Toolkit and Finite State Machine (FSM) Built-ins."""

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


def test_smc_window_builtin():
    code = """
    var text = "ABCDEF"
    var win3 = window(text, 3, 1)
    var win2_step2 = window(text, 2, 2)
    var list_data = [10, 20, 30, 40, 50]
    var list_win = window(list_data, 2, 1)
    """
    vm = run_code(code)
    assert vm.get_var("win3") == ["ABC", "BCD", "CDE", "DEF"]
    assert vm.get_var("win2_step2") == ["AB", "CD", "EF"]
    assert vm.get_var("list_win") == [[10, 20], [20, 30], [30, 40], [40, 50]]


def test_smc_count_matches():
    code = """
    var text = "ATGCGATCGTATCG"
    var cg_count = count_matches(text, "CG")
    var a_count = count_matches(text, "A")
    """
    vm = run_code(code)
    assert vm.get_var("cg_count") == 3
    assert vm.get_var("a_count") == 3


def test_smc_clamp_and_round():
    code = """
    var c1 = clamp(150, 0, 100)
    var c2 = clamp(-25, 0, 100)
    var c3 = clamp(42, 0, 100)
    var r1 = round(3.14159, 2)
    var r2 = round(4.8)
    """
    vm = run_code(code)
    assert vm.get_var("c1") == 100.0
    assert vm.get_var("c2") == 0.0
    assert vm.get_var("c3") == 42.0
    assert vm.get_var("r1") == 3.14
    assert vm.get_var("r2") == 5


def test_smc_fsm_builtins():
    code = """
    var fsm_table = {
        "IDLE": {"START": "ACTIVE", "SHUTDOWN": "OFF"},
        "ACTIVE": {"STOP": "IDLE", "ERROR": "STALLED"},
        "STALLED": {"RESET": "IDLE"}
    }
    var next_s1 = fsm_transition("IDLE", "START", fsm_table)
    var next_s2 = fsm_transition("ACTIVE", "ERROR", fsm_table)
    var unhandled = fsm_transition("IDLE", "UNKNOWN_EVENT", fsm_table)

    # Multi-step run simulation
    var event_stream = ["START", "ERROR", "RESET", "START", "STOP"]
    var sim_res = fsm_run("IDLE", event_stream, fsm_table)
    """
    vm = run_code(code)
    assert vm.get_var("next_s1") == "ACTIVE"
    assert vm.get_var("next_s2") == "STALLED"
    assert vm.get_var("unhandled") == "IDLE"
    
    sim = vm.get_var("sim_res")
    assert sim["final_state"] == "IDLE"
    assert sim["history"] == ["IDLE", "ACTIVE", "STALLED", "IDLE", "ACTIVE", "IDLE"]

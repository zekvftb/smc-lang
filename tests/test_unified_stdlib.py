"""Unit tests for SMC Unified Fast Bytecode Runtime and Standard Library."""

import pytest
from smc.compiler import BytecodeCompiler
from smc.bytecode_vm import BytecodeVM
from smc.lexer import SmcLexer
from smc.parser import SmcParser


def compile_and_run(code: str, strict: bool = False) -> BytecodeVM:
    lexer = SmcLexer(code, strict=strict)
    tokens = lexer.tokenize()
    ast = SmcParser(tokens).parse()
    compiler = BytecodeCompiler()
    chunk = compiler.compile(ast)
    vm = BytecodeVM()
    vm.run(chunk)
    return vm


def test_stdlib_math_functions():
    code = """
    func mean(numbers) {
        if len(numbers) == 0 {
            return 0.0
        }
        var total = 0.0
        for n in numbers {
            total += n
        }
        return total / len(numbers)
    }

    var data = [10.0, 20.0, 30.0, 40.0]
    var avg = mean(data)
    """
    vm = compile_and_run(code, strict=True)
    assert vm.globals["avg"] == 25.0


def test_stdlib_fsm_validation():
    code = """
    var fsm = {
        "A": {"NEXT": "B"},
        "B": {"BACK": "A"}
    }
    var state_names = keys(fsm)
    var trans_a = fsm["A"]
    var target = trans_a["NEXT"]
    var is_target_valid = contains(state_names, target)
    """
    vm = compile_and_run(code, strict=True)
    assert vm.globals["is_target_valid"] is True


def test_stdlib_sequence_gc_calculation():
    code = """
    var dna = "ATGCGCGCAT"
    var g_count = count_matches(dna, "G")
    var c_count = count_matches(dna, "C")
    var total_gc = g_count + c_count
    var gc_pct = round((total_gc * 100.0) / len(dna), 1)
    """
    vm = compile_and_run(code, strict=False)
    assert vm.globals["gc_pct"] == 60.0

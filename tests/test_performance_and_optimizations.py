"""Unit tests for SMC Compiler Optimizations, Constant Folding, and Runtime Reliability."""

import time
import pytest
from smc.compiler import BytecodeCompiler, BytecodeOp, PeepholeOptimizer, Instruction
from smc.bytecode_vm import BytecodeVM
from smc.lexer import SmcLexer
from smc.parser import SmcParser


def compile_and_get_instructions(code: str, optimize: bool = True) -> list[Instruction]:
    tokens = SmcLexer(code).tokenize()
    ast = SmcParser(tokens).parse()
    compiler = BytecodeCompiler(optimize=optimize)
    chunk = compiler.compile(ast)
    return chunk.instructions


def test_peephole_constant_folding_math():
    code = "var result = (10 + 20) * 3 - 5"
    insts = compile_and_get_instructions(code, optimize=True)
    # The entire expression (10 + 20) * 3 - 5 should be folded into 85!
    # Expected instructions: LOAD_CONST 85, STORE_VAR 'result', HALT
    assert len(insts) == 3
    assert insts[0].op == BytecodeOp.LOAD_CONST
    assert insts[0].operand == 85
    assert insts[1].op == BytecodeOp.STORE_VAR
    assert insts[1].operand == "result"


def test_peephole_constant_folding_strings():
    code = 'var greeting = "Hello " + "World"'
    insts = compile_and_get_instructions(code, optimize=True)
    assert len(insts) == 3
    assert insts[0].operand == "Hello World"


def test_bytecode_recursion_depth_limit():
    code = """
    func runaway(n) {
        return runaway(n + 1)
    }
    var crash = runaway(1)
    """
    tokens = SmcLexer(code).tokenize()
    ast = SmcParser(tokens).parse()
    chunk = BytecodeCompiler().compile(ast)
    vm = BytecodeVM()
    with pytest.raises(RecursionError, match="Maximum call stack depth of 500 exceeded"):
        vm.run(chunk)


def test_high_throughput_execution_benchmark():
    code = """
    var sum = 0
    var i = 0
    while i < 10000 {
        sum += i
        i += 1
    }
    """
    tokens = SmcLexer(code).tokenize()
    ast = SmcParser(tokens).parse()
    chunk = BytecodeCompiler().compile(ast)
    vm = BytecodeVM()

    start = time.perf_counter()
    res = vm.run(chunk)
    elapsed = time.perf_counter() - start

    assert vm.globals["sum"] == 49995000
    assert vm.globals["i"] == 10000
    # Ensure 10,000 iterations execute in well under 0.5 seconds
    assert elapsed < 0.5, f"10,000 iterations took {elapsed:.3f}s (expected < 0.5s)"

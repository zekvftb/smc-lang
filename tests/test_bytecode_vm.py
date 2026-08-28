"""Unit tests for SMC Linear Bytecode Compiler, Stack VM, and Strict Mode."""

import pytest
from smc.compiler import BytecodeCompiler, BytecodeOp
from smc.bytecode_vm import BytecodeVM
from smc.lexer import SmcLexer
from smc.parser import SmcParser


def compile_and_run_bytecode(code: str, strict: bool = False) -> BytecodeVM:
    lexer = SmcLexer(code, strict=strict)
    tokens = lexer.tokenize()
    ast = SmcParser(tokens).parse()
    compiler = BytecodeCompiler()
    chunk = compiler.compile(ast)
    vm = BytecodeVM()
    vm.run(chunk)
    return vm


def test_bytecode_arithmetic_and_variables():
    code = """
    var a = 10
    var b = 25
    var sum = a + b * 2
    var diff = sum - 10
    var is_greater = sum > 50
    """
    vm = compile_and_run_bytecode(code)
    assert vm.globals["a"] == 10
    assert vm.globals["b"] == 25
    assert vm.globals["sum"] == 60
    assert vm.globals["diff"] == 50
    assert vm.globals["is_greater"] is True


def test_bytecode_if_else_control_flow():
    code = """
    var x = 42
    var branch = "none"
    if x > 50 {
        branch = "high"
    } else {
        branch = "low"
    }
    """
    vm = compile_and_run_bytecode(code)
    assert vm.globals["branch"] == "low"


def test_bytecode_while_loop():
    code = """
    var counter = 0
    var accumulator = 0
    while counter < 100 {
        accumulator += counter
        counter += 1
    }
    """
    vm = compile_and_run_bytecode(code)
    assert vm.globals["counter"] == 100
    assert vm.globals["accumulator"] == 4950


def test_bytecode_user_functions():
    code = """
    func multiply(x, y) {
        return x * y
    }
    var product = multiply(7, 8)
    """
    vm = compile_and_run_bytecode(code)
    assert vm.globals["product"] == 56


def test_strict_mode_keyword_enforcement():
    # In fault-tolerant mode, "prnt" resolves to PRINT via codon wobble
    lenient_code = 'prnt "Hello"'
    tokens_lenient = SmcLexer(lenient_code, strict=False).tokenize()
    assert tokens_lenient[0].was_mutated is True

    # In strict mode, "prnt" is treated as an identifier (not resolved as PRINT keyword)
    tokens_strict = SmcLexer(lenient_code, strict=True).tokenize()
    assert tokens_strict[0].token_type.value == "IDENTIFIER"

    # In strict mode, invalid characters raise SyntaxError
    with pytest.raises(SyntaxError):
        SmcLexer('var x = 10 $', strict=True).tokenize()

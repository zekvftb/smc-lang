"""Unit tests for Stage 3: User Functions, Return Values, Scopes, and Lists."""

import pytest

from smc.lexer import SmcLexer
from smc.parser import SmcParser
from smc.vm import DexterVM


def run_code(code: str) -> dict:
    tokens = SmcLexer(code).tokenize()
    ast = SmcParser(tokens).parse()
    vm = DexterVM()
    return vm.run(ast)


def test_function_params_and_return():
    """Verify parameterized functions execute and return correct values."""
    code = (
        "fn multiply_and_add(a, b, c) {\n"
        "    let result = (a * b) + c\n"
        "    return result\n"
        "}\n"
        "let answer = multiply_and_add(5, 4, 3)\n"
        "halt\n"
    )
    res = run_code(code)
    # (5 * 4) + 3 = 23
    assert res["final_variables"]["answer"] == 23


def test_function_scope_isolation():
    """Verify local variables inside functions do not overwrite global variables."""
    code = (
        "let shadow_var = 100\n"
        "fn mutate_scope() {\n"
        "    let shadow_var = 999\n"
        "    return shadow_var\n"
        "}\n"
        "let returned = mutate_scope()\n"
        "halt\n"
    )
    res = run_code(code)
    # Function should return local 999, but global shadow_var must remain 100
    assert res["final_variables"]["returned"] == 999
    assert res["final_variables"]["shadow_var"] == 100


def test_first_class_lists_and_indexing():
    """Verify list literals and element indexing."""
    code = (
        "let items = ['Potion', 'Shield', 'Sword']\n"
        "let numbers = [10, 20 + 5, 50 * 2]\n"
        "let item0 = items[0]\n"
        "let num1 = numbers[1]\n"
        "let num2 = numbers[2]\n"
        "halt\n"
    )
    res = run_code(code)
    vars = res["final_variables"]
    assert vars["item0"] == "Potion"
    assert vars["num1"] == 25
    assert vars["num2"] == 100


def test_nested_function_calls():
    """Verify functions can call other functions recursively or in composition."""
    code = (
        "fn double_val(x) {\n"
        "    return x * 2\n"
        "}\n"
        "fn quad_val(x) {\n"
        "    let step1 = double_val(x)\n"
        "    let step2 = double_val(step1)\n"
        "    return step2\n"
        "}\n"
        "let total = quad_val(7)\n"
        "halt\n"
    )
    res = run_code(code)
    # 7 * 2 = 14, 14 * 2 = 28
    assert res["final_variables"]["total"] == 28

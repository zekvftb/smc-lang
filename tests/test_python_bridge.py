"""Automated unit tests for SMC Python Bridge (FFI) capabilities."""

import pytest

from smc.lexer import SmcLexer
from smc.parser import SmcParser
from smc.vm import DexterVM


def test_py_call_standard_library():
    """Verify py_call can invoke functions from math, random, and string modules."""
    code = (
        'let root = py_call("math.sqrt", 144)\n'
        'let power = py_call("math.pow", 2, 8)\n'
        'let roll = py_call("random.randint", 10, 20)\n'
        'halt\n'
    )
    tokens = SmcLexer(code).tokenize()
    ast = SmcParser(tokens).parse()
    vm = DexterVM()
    res = vm.run(ast)

    vars = res["final_variables"]
    assert vars["root"] == 12.0
    assert vars["power"] == 256.0
    assert 10 <= vars["roll"] <= 20


def test_py_import_module_and_alias():
    """Verify py_import statement loads modules into DexterVM scope."""
    code = (
        'py_import "math"\n'
        'py_import "datetime" as dt\n'
        'let sin_val = py_call("math.sin", 0)\n'
        'let direct_sqrt = py_call("sqrt", 81)\n'
        'let year_num = py_eval("dt.date(2026, 8, 27).year")\n'
        'halt\n'
    )
    tokens = SmcLexer(code).tokenize()
    ast = SmcParser(tokens).parse()
    vm = DexterVM()
    res = vm.run(ast)

    vars = res["final_variables"]
    assert vars["sin_val"] == 0.0
    assert vars["direct_sqrt"] == 9.0
    assert vars["year_num"] == 2026
    assert any("Successfully loaded Python module 'math'" in line for line in res["stdout"])
    assert any("Successfully loaded Python module 'datetime' as 'dt'" in line for line in res["stdout"])


def test_py_eval_expressions():
    """Verify py_eval can evaluate Python expressions and return marshalled data."""
    code = (
        'let total = py_eval("sum([10, 20, 30, 40])")\n'
        'let formatted = py_eval("\'hello world\'.title()")\n'
        'let dict_data = py_eval("{\'a\': 1, \'b\': [2, 3]}")\n'
        'halt\n'
    )
    tokens = SmcLexer(code).tokenize()
    ast = SmcParser(tokens).parse()
    vm = DexterVM()
    res = vm.run(ast)

    vars = res["final_variables"]
    assert vars["total"] == 100
    assert vars["formatted"] == "Hello World"
    assert vars["dict_data"] == {"a": 1, "b": [2, 3]}


def test_py_bridge_fault_tolerance():
    """Verify that Python errors or missing modules are caught gracefully without crashing."""
    code = (
        'let bad_call = py_call("nonexistent_package.fake_func", 123)\n'
        'let bad_eval = py_eval("1 / 0")\n'
        'let alive = true\n'
        'halt\n'
    )
    tokens = SmcLexer(code).tokenize()
    ast = SmcParser(tokens).parse()
    vm = DexterVM()
    res = vm.run(ast)

    vars = res["final_variables"]
    assert vars["alive"] is True
    assert any("[PY_BRIDGE_ERROR]" in line for line in res["stdout"])

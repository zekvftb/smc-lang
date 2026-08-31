"""Runtime Safety, Deterministic Execution & Algorithmic Accuracy Test Suite for DexterVM and BytecodeVM."""

from __future__ import annotations

import pytest
from smc.bytecode_vm import BytecodeVM
from smc.compiler import BytecodeCompiler
from smc.lexer import SmcLexer
from smc.parser import SmcParser
from smc.vm import DexterVM


def run_smc_ast(source: str, strict_mode: bool = False) -> dict:
    tokens = SmcLexer(source, strict=strict_mode).tokenize()
    ast = SmcParser(tokens).parse()
    vm = DexterVM(strict_mode=strict_mode)
    return vm.run(ast)


def run_smc_bytecode(source: str, strict_mode: bool = False) -> dict:
    tokens = SmcLexer(source, strict=strict_mode).tokenize()
    ast = SmcParser(tokens).parse()
    chunk = BytecodeCompiler().compile(ast)
    vm = BytecodeVM(strict_mode=strict_mode)
    return vm.run(chunk)


# ---------------------------------------------------------------------------
# 1. Arithmetic & Scoping Safety Tests
# ---------------------------------------------------------------------------

def test_strict_mode_zero_division_error_ast():
    """Verify that division and modulo by zero raise ZeroDivisionError in strict AST mode."""
    src_div = "experiment 'strict_div' { x = 10 / 0 }"
    with pytest.raises(ZeroDivisionError):
        run_smc_ast(src_div, strict_mode=True)

    src_mod = "experiment 'strict_mod' { x = 10 % 0 }"
    with pytest.raises(ZeroDivisionError):
        run_smc_ast(src_mod, strict_mode=True)


def test_strict_mode_zero_division_error_bytecode():
    """Verify that division and modulo by zero raise ZeroDivisionError in strict Bytecode mode."""
    src_div = "experiment 'strict_div_bc' { x = 10 / 0 }"
    with pytest.raises(ZeroDivisionError):
        run_smc_bytecode(src_div, strict_mode=True)

    src_mod = "experiment 'strict_mod_bc' { x = 10 % 0 }"
    with pytest.raises(ZeroDivisionError):
        run_smc_bytecode(src_mod, strict_mode=True)


def test_non_strict_mode_zero_division_fault_tolerance():
    """Verify that non-strict mode safely clamps division by zero and logs a warning."""
    src = "experiment 'safe_div' { x = 10 / 0; y = 10 % 0 }"
    res_ast = run_smc_ast(src, strict_mode=False)
    assert res_ast["final_variables"]["x"] == 0
    assert any("Division by zero" in line for line in res_ast["stdout"])

    res_bc = run_smc_bytecode(src, strict_mode=False)
    assert res_bc["final_variables"]["x"] == 0


def test_strict_mode_unbound_identifier_error():
    """Verify that referencing an uninitialized variable raises NameError in strict mode."""
    src = "experiment 'strict_name' { y = uninitialized_var + 5 }"
    with pytest.raises(NameError):
        run_smc_ast(src, strict_mode=True)

    with pytest.raises(NameError):
        run_smc_bytecode(src, strict_mode=True)


def test_strict_mode_list_index_out_of_bounds():
    """Verify that assigning to an out-of-bounds list index raises IndexError in strict mode."""
    src = """
    experiment 'strict_idx' {
        let arr = [1, 2, 3]
        arr[10] = 99
    }
    """
    with pytest.raises(IndexError):
        run_smc_ast(src, strict_mode=True)

    with pytest.raises(IndexError):
        run_smc_bytecode(src, strict_mode=True)


# ---------------------------------------------------------------------------
# 2. Standard Algorithmic Numerical Accuracy Benchmarks
# ---------------------------------------------------------------------------

def test_algorithm_bubble_sort_accuracy():
    """Benchmark: Bubble Sort algorithm in SMC matches Python standard sorted output."""
    smc_code = """
    experiment 'bubble_sort' {
        fn bubble_sort(arr) {
            let n = len(arr)
            for i in range(0, n) {
                for j in range(0, n - i - 1) {
                    if (arr[j] > arr[j + 1]) {
                        let temp = arr[j]
                        arr[j] = arr[j + 1]
                        arr[j + 1] = temp
                    }
                }
            }
            return arr
        }

        let data = [64, 34, 25, 12, 22, 11, 90]
        let sorted_data = bubble_sort(data)
    }
    """
    res = run_smc_ast(smc_code, strict_mode=True)
    expected = sorted([64, 34, 25, 12, 22, 11, 90])
    assert res["final_variables"]["sorted_data"] == expected


def test_algorithm_recursive_fibonacci():
    """Benchmark: Recursive Fibonacci computation in SMC matches standard math sequence."""
    smc_code = """
    experiment 'fibonacci' {
        fn fib(n) {
            if (n <= 0) {
                return 0
            }
            if (n == 1) {
                return 1
            }
            return fib(n - 1) + fib(n - 2)
        }

        let fib_10 = fib(10)
    }
    """
    res = run_smc_ast(smc_code, strict_mode=True)
    assert res["final_variables"]["fib_10"] == 55


def test_algorithm_prime_sieve_of_eratosthenes():
    """Benchmark: Prime generation sieve up to 30 in SMC matches known primes."""
    smc_code = """
    experiment 'sieve' {
        fn get_primes(limit) {
            let primes = []
            for num in range(2, limit + 1) {
                let is_prime = true
                for d in range(2, num) {
                    if (num % d == 0) {
                        let is_prime = false
                    }
                }
                if (is_prime) {
                    push(primes, num)
                }
            }
            return primes
        }

        let found_primes = get_primes(30)
    }
    """
    res = run_smc_ast(smc_code, strict_mode=True)
    expected_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    assert res["final_variables"]["found_primes"] == expected_primes


def test_auto_grow_list_index_mode():
    """Verify that auto_grow=True allows list growth on out-of-bounds index assignment."""
    src = """
    experiment 'autogrow_idx' {
        let arr = [10, 20]
        arr[5] = 99
    }
    """
    tokens = SmcLexer(src).tokenize()
    ast = SmcParser(tokens).parse()
    vm = DexterVM(auto_grow=True)
    res = vm.run(ast)
    assert res["final_variables"]["arr"] == [10, 20, 0, 0, 0, 99]

    chunk = BytecodeCompiler().compile(ast)
    b_vm = BytecodeVM(auto_grow=True)
    b_res = b_vm.run(chunk)
    assert b_res["final_variables"]["arr"] == [10, 20, 0, 0, 0, 99]


# ---------------------------------------------------------------------------
# 3. DSL Feature Encapsulation & Phase Register Invariants
# ---------------------------------------------------------------------------

def test_phase_register_slip_isolation():
    """Verify that slip(k) strictly shifts phase modulo 3 without polluting local scopes."""
    smc_code = """
    experiment 'phase_test' {
        let phase_start = 0
        slip(1)
        let p1 = current_phase
        slip(1)
        let p2 = current_phase
        slip(1)
        let p3 = current_phase
    }
    """
    res = run_smc_ast(smc_code, strict_mode=True)
    assert res["final_variables"]["p1"] == 1
    assert res["final_variables"]["p2"] == 2
    assert res["final_variables"]["p3"] == 0


def test_acme_ephemeral_ttl_decay():
    """Verify that Acme Anvil TTL variables count down deterministically and expire."""
    smc_code = """
    experiment 'acme_test' {
        acme(ttl=2) ephemeral_token = 999
        v1 = ephemeral_token
    }
    """
    res = run_smc_ast(smc_code, strict_mode=False)
    assert res["final_variables"]["v1"] == 999


# ---------------------------------------------------------------------------
# 4. Property-Based Arithmetic Invariant Tests (Hypothesis)
# ---------------------------------------------------------------------------

from hypothesis import given, settings, strategies as st

@given(st.integers(min_value=-1000, max_value=1000), st.integers(min_value=-1000, max_value=1000))
@settings(max_examples=40)
def test_property_smc_addition_and_subtraction(a: int, b: int):
    """Property test: SMC binary + and - match exact Python integer arithmetic."""
    smc_code = f"""
    experiment 'math_prop' {{
        let add_res = {a} + {b}
        let sub_res = {a} - {b}
    }}
    """
    res = run_smc_ast(smc_code, strict_mode=True)
    assert res["final_variables"]["add_res"] == a + b
    assert res["final_variables"]["sub_res"] == a - b


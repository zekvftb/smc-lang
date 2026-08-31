"""Test Suite for Genetic Programming AST Evolution and Chaos Engineering in SMC."""

from __future__ import annotations

import pytest

from smc.chaos import ChaosHarness
from smc.evolution import GeneticOptimizer, Individual


def test_genetic_evolution_target_convergence():
    """Verify that Genetic Programming evolves an AST program toward target value 42."""
    optimizer = GeneticOptimizer(population_size=15, mutation_rate=0.4, seed=42)

    # Fitness function: minimize distance from target result 42
    def fitness_fn(vars_dict: dict) -> float:
        res = vars_dict.get("result", 0)
        if not isinstance(res, (int, float)):
            return -1000.0
        # Negative absolute error
        return -abs(res - 42)

    best_ind = optimizer.evolve(generations=6, fitness_fn=fitness_fn)

    assert best_ind is not None
    assert best_ind.fitness > -50.0
    assert len(optimizer.history) == 6
    assert "experiment" in best_ind.source_code


def test_genetic_evolution_seeded_determinism():
    """Verify that identical seeds produce bitwise-identical evolutionary runs."""
    def fitness_fn(vars_dict: dict) -> float:
        return float(vars_dict.get("result", 0))

    opt1 = GeneticOptimizer(population_size=10, seed=12345)
    best1 = opt1.evolve(generations=4, fitness_fn=fitness_fn)

    opt2 = GeneticOptimizer(population_size=10, seed=12345)
    best2 = opt2.evolve(generations=4, fitness_fn=fitness_fn)

    assert best1.source_code == best2.source_code
    assert best1.fitness == best2.fitness
    assert [h["best_fitness"] for h in opt1.history] == [h["best_fitness"] for h in opt2.history]


def test_chaos_ttl_token_lifecycle():
    """Verify that Acme Anvil TTL tokens expire deterministically after configured cycles."""
    harness = ChaosHarness(seed=42)
    res = harness.run_ttl_token_lifecycle(token_ttl=2, cycles=4)

    assert res["initial_value"] == 777
    assert res["final_value"] == 0
    assert res["expired"] is True
    assert res["anvils_dropped"] >= 1


def test_chaos_watchdog_fault_recovery():
    """Verify that Tuxedo Mask fallback handler intercepts chaos-injected unbound rings."""
    harness = ChaosHarness(seed=42)
    report = harness.run_watchdog_fault_injection(trials=10, fault_probability=0.8)

    assert report.trials_run == 10
    assert report.faults_injected > 0
    assert report.recovery_rate_pct == 100.0
    assert report.faults_recovered == report.faults_injected

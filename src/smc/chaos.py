"""Chaos Resilience & Ephemeral Lifecycle Utilities for SMC.

Provides automated chaos fault injection (latency simulation, state corruption,
ephemeral TTL token expiration, and watchdog fallback recovery) for SMC systems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import random
import time
from typing import Any

from smc.lexer import SmcLexer
from smc.parser import SmcParser
from smc.vm import DexterVM


@dataclass
class ChaosReport:
    """Outcome of a chaos engineering resilience experiment."""

    experiment_name: str
    trials_run: int
    faults_injected: int
    faults_recovered: int
    anvils_dropped: int
    recovery_rate_pct: float
    trace_log: list[str] = field(default_factory=list)


class ChaosHarness:
    """Deterministic fault-injection and resilience testing harness for SMC programs."""

    def __init__(self, seed: int = 42) -> None:
        self.rng = random.Random(seed)

    def run_ttl_token_lifecycle(
        self,
        token_ttl: int = 3,
        cycles: int = 5,
    ) -> dict[str, Any]:
        """Test ephemeral token expiration and renewal lifecycle using acme(ttl=N)."""
        smc_code = f"""
        experiment 'token_lifecycle' {{
            acme(ttl={token_ttl}) session_auth = 777
            let token_val = session_auth
        }}
        """
        tokens = SmcLexer(smc_code).tokenize()
        ast = SmcParser(tokens).parse()
        vm = DexterVM()

        # Step 1: Initialize
        vm.run(ast)
        t1 = vm.get_var("session_auth")
        
        # Step 2: Manually tick cycles
        status_log = [f"Initial token: {t1}"]
        for c in range(1, cycles + 1):
            vm.execution_steps += 1
            vm._tick_acme_ttls()
            curr = vm.get_var("session_auth")
            status_log.append(f"Cycle {c}: session_auth={curr}")

        return {
            "initial_value": t1,
            "final_value": vm.get_var("session_auth"),
            "anvils_dropped": vm.anvils_dropped,
            "expired": vm.get_var("session_auth") == 0,
            "trace": status_log,
        }

    def run_watchdog_fault_injection(
        self,
        trials: int = 10,
        fault_probability: float = 0.5,
    ) -> ChaosReport:
        """Inject random missing ring dispatch calls and verify Tuxedo Mask fallback recovery."""
        smc_code = """
        experiment 'watchdog_chaos' {
            fallback {
                let recovery_flag = 1
                print 'WATCHDOG_INTERCEPTED'
            }

            summon FIRE {
                let status = 'FIRE_ACTIVE'
            }
        }
        """
        tokens = SmcLexer(smc_code).tokenize()
        ast = SmcParser(tokens).parse()

        faults_injected = 0
        faults_recovered = 0
        trace = []

        for t in range(trials):
            vm = DexterVM()
            vm.run(ast)

            # Injected chaos dispatch
            if self.rng.random() < fault_probability:
                faults_injected += 1
                # Call invalid ring
                bad_ring = f"INVALID_RING_{t}"
                trace.append(f"[CHAOS_INJECT] Calling non-existent ring '{bad_ring}'")
                
                # Execute node call_ring
                from smc.parser import CallRingNode
                vm.execute_node(CallRingNode(ring=bad_ring))

                if vm.get_var("recovery_flag") == 1:
                    faults_recovered += 1
                    trace.append("[CHAOS_RECOVER] Tuxedo Mask watchdog successfully recovered.")

        recovery_rate = round((faults_recovered / max(1, faults_injected)) * 100.0, 2)

        return ChaosReport(
            experiment_name="watchdog_chaos",
            trials_run=trials,
            faults_injected=faults_injected,
            faults_recovered=faults_recovered,
            anvils_dropped=0,
            recovery_rate_pct=recovery_rate,
            trace_log=trace,
        )

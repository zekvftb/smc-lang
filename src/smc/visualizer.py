"""Interactive Multi-Phase Execution Visualizer & Event Emitter for SMC.

Renders ASCII terminal traces of active reading phases (Phi = 0, 1, 2),
call frames, and Acme TTL countdown clocks, and exports JSON traces for web UIs.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Any

from smc.lexer import SmcLexer
from smc.parser import AstNode, ProgramNode, SetVarNode, SlipNode, SmcParser
from smc.vm import DexterVM


@dataclass
class TraceStep:
    """A single discrete execution step in the multi-phase VM trace."""

    step_index: int
    active_phase: int
    phase_diagram: str
    instruction_desc: str
    variables_snapshot: dict[str, Any]
    acme_ttl_snapshot: dict[str, int]
    call_stack_depth: int


class MultiPhaseVisualizer:
    """Interactive terminal formatter and web event exporter for DexterVM executions."""

    @staticmethod
    def render_phase_diagram(phase: int) -> str:
        """Render a 3-track ASCII diagram highlighting the active phase."""
        p0 = "[+0: ACTIVE]" if phase == 0 else "[+0: idle  ]"
        p1 = "[+1: ACTIVE]" if phase == 1 else "[+1: idle  ]"
        p2 = "[+2: ACTIVE]" if phase == 2 else "[+2: idle  ]"
        return f"{p0} === {p1} === {p2}"

    @classmethod
    def trace_execution(cls, source_code: str) -> list[TraceStep]:
        """Execute source step-by-step and capture complete multi-phase trace history."""
        tokens = SmcLexer(source_code).tokenize()
        ast = SmcParser(tokens).parse()
        vm = DexterVM()

        steps: list[TraceStep] = []
        step_idx = 0

        for stmt in ast.statements:
            step_idx += 1
            vm.execute_node(stmt)

            phase = vm.current_phase_offset
            diagram = cls.render_phase_diagram(phase)
            desc = stmt.__class__.__name__
            if isinstance(stmt, SetVarNode):
                desc = f"LET {stmt.name} = <expr>"
            elif isinstance(stmt, SlipNode):
                desc = f"SLIP({phase})"

            ttl_snap = {k: v.ttl for k, v in vm.ttl_memory.items()}

            steps.append(
                TraceStep(
                    step_index=step_idx,
                    active_phase=phase,
                    phase_diagram=diagram,
                    instruction_desc=desc,
                    variables_snapshot=dict(vm.variables),
                    acme_ttl_snapshot=ttl_snap,
                    call_stack_depth=len(vm.call_stack),
                )
            )

        return steps

    @classmethod
    def render_ascii_trace(cls, source_code: str) -> str:
        """Render full ASCII execution summary with phase track transitions."""
        steps = cls.trace_execution(source_code)
        lines = [
            "=" * 70,
            "🧬 SMC DEXTER-VM MULTI-PHASE EXECUTION TRACE",
            "=" * 70,
        ]

        for s in steps:
            lines.append(f"Step {s.step_index:02d} | Phase +{s.active_phase} | {s.phase_diagram}")
            lines.append(f"        -> Op: {s.instruction_desc}")
            if s.variables_snapshot:
                var_str = ", ".join(f"{k}={v}" for k, v in s.variables_snapshot.items())
                lines.append(f"        -> Scope: {var_str}")
            if s.acme_ttl_snapshot:
                ttl_str = ", ".join(f"{k}(ttl={v})" for k, v in s.acme_ttl_snapshot.items())
                lines.append(f"        -> Acme TTLs: {ttl_str}")
            lines.append("-" * 70)

        return "\n".join(lines)

    @classmethod
    def export_json_trace(cls, source_code: str) -> str:
        """Export execution trace as a web-compatible JSON event stream."""
        steps = cls.trace_execution(source_code)
        return json.dumps([asdict(s) for s in steps], indent=2)

    @staticmethod
    def render_fitness_sparkline(fitness_history: list[float], width: int = 20) -> str:
        """Render an ASCII sparkline representing evolutionary fitness convergence."""
        if not fitness_history:
            return "[No history]"
        min_v = min(fitness_history)
        max_v = max(fitness_history)
        rng = max(1e-6, max_v - min_v)
        bars = " ▂▃▄▅▆▇█"

        spark = []
        for val in fitness_history:
            idx = int(((val - min_v) / rng) * (len(bars) - 1))
            spark.append(bars[idx])
        return "".join(spark)

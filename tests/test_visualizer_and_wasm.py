"""Test Suite for Multi-Phase Execution Visualizer and WASM Compiler Bridge."""

from __future__ import annotations

import json
import pytest

from smc.visualizer import MultiPhaseVisualizer
from smc.wasm_runner import WasmCompilerBridge


def test_multiphase_visualizer_trace():
    """Verify visualizer captures step-by-step state transitions and phase register shifts."""
    smc_code = """
    experiment 'vis_test' {
        let x = 10
        slip(1)
        let y = x + 20
        slip(1)
        acme(ttl=3) temp_flag = 1
        slip(1)
    }
    """
    steps = MultiPhaseVisualizer.trace_execution(smc_code)
    assert len(steps) == 6

    # Verify phase state transitions
    assert steps[0].active_phase == 0
    assert steps[1].active_phase == 1
    assert steps[2].active_phase == 1
    assert steps[3].active_phase == 2
    assert steps[4].active_phase == 2
    assert steps[5].active_phase == 0

    assert "ACTIVE" in steps[1].phase_diagram
    assert steps[4].acme_ttl_snapshot.get("temp_flag") == 3


def test_visualizer_ascii_and_json_export():
    """Verify ASCII formatting and JSON event stream generation."""
    smc_code = """
    experiment 'export_test' {
        let a = 1
        slip(1)
        let b = 2
    }
    """
    ascii_out = MultiPhaseVisualizer.render_ascii_trace(smc_code)
    assert "🧬 SMC DEXTER-VM MULTI-PHASE EXECUTION TRACE" in ascii_out
    assert "Phase +1" in ascii_out

    json_out = MultiPhaseVisualizer.export_json_trace(smc_code)
    parsed = json.loads(json_out)
    assert isinstance(parsed, list)
    assert len(parsed) == 3
    assert parsed[1]["active_phase"] == 1


def test_fitness_sparkline_rendering():
    """Verify generation of ASCII sparklines for evolutionary progress."""
    history = [-100.0, -80.0, -50.0, -20.0, -5.0, 0.0]
    spark = MultiPhaseVisualizer.render_fitness_sparkline(history)
    assert len(spark) == len(history)
    assert spark[-1] == "█"


def test_wasm_compiler_bridge_package():
    """Verify WASM JSON package compilation and instruction bundling."""
    smc_code = """
    experiment 'wasm_app' {
        let sum = 0
        for i in range(1, 5) {
            sum += i
        }
    }
    """
    pkg = WasmCompilerBridge.compile_to_wasm_package(smc_code)
    assert pkg.version == "1.0.0-WASM"
    assert pkg.program_name == "wasm_app"
    assert pkg.instruction_count > 0
    assert len(pkg.instructions) == pkg.instruction_count

    json_str = pkg.to_json()
    assert "wasm_app" in json_str


def test_wasm_benchmark_submillisecond_throughput():
    """Verify bytecode VM achieves sub-millisecond execution throughput."""
    smc_code = """
    experiment 'bench_app' {
        let acc = 0
        acc += 10
        acc -= 5
        acc *= 2
    }
    """
    bench = WasmCompilerBridge.benchmark_execution_speed(smc_code, iterations=50)
    assert bench["iterations"] == 50
    assert bench["sub_millisecond_compliant"] is True
    assert bench["throughput_ops_per_ms"] > 0

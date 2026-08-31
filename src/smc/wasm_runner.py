"""WebAssembly & Browser-Ready Zero-Dependency Execution Runner for SMC Bytecode.

Provides compact JSON bytecode serialization for Pyodide/browser execution,
alongside sub-millisecond execution throughput benchmarking.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import time
from typing import Any

from smc.bytecode_vm import BytecodeVM
from smc.compiler import BytecodeChunk, BytecodeCompiler, Instruction
from smc.lexer import SmcLexer
from smc.parser import SmcParser


@dataclass
class WasmPackage:
    """Zero-dependency browser/WASM-ready bytecode bundle."""

    version: str
    program_name: str
    instructions: list[dict[str, Any]]
    instruction_count: int
    constants_pool: list[Any]

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


class WasmCompilerBridge:
    """Serializes compiled SMC bytecode chunks for in-browser WASM and Pyodide runtimes."""

    @staticmethod
    def compile_to_wasm_package(source_code: str) -> WasmPackage:
        """Compile SMC source code into a portable JSON package for WASM/Pyodide."""
        tokens = SmcLexer(source_code).tokenize()
        ast = SmcParser(tokens).parse()
        chunk = BytecodeCompiler().compile(ast)

        inst_list = []
        constants = []

        for inst in chunk.instructions:
            inst_list.append({
                "op": inst.op.name,
                "operand": inst.operand,
            })
            if inst.operand is not None and inst.operand not in constants:
                constants.append(inst.operand)

        return WasmPackage(
            version="1.0.0-WASM",
            program_name=ast.name,
            instructions=inst_list,
            instruction_count=len(inst_list),
            constants_pool=constants,
        )

    @staticmethod
    def benchmark_execution_speed(source_code: str, iterations: int = 100) -> dict[str, Any]:
        """Benchmark bytecode execution throughput (operations per millisecond)."""
        tokens = SmcLexer(source_code).tokenize()
        ast = SmcParser(tokens).parse()
        chunk = BytecodeCompiler().compile(ast)

        t_start = time.perf_counter()
        vm = BytecodeVM()
        for _ in range(iterations):
            vm = BytecodeVM()
            vm.run(chunk)
        t_end = time.perf_counter()

        total_elapsed_ms = (t_end - t_start) * 1000.0
        avg_ms_per_run = total_elapsed_ms / iterations
        total_instructions = len(chunk.instructions) * iterations
        ops_per_ms = total_instructions / max(1e-6, total_elapsed_ms)

        return {
            "iterations": iterations,
            "total_elapsed_ms": round(total_elapsed_ms, 3),
            "avg_ms_per_run": round(avg_ms_per_run, 4),
            "total_instructions_executed": total_instructions,
            "throughput_ops_per_ms": round(ops_per_ms, 2),
            "sub_millisecond_compliant": avg_ms_per_run < 1.0,
        }

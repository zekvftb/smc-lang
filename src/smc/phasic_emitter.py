"""Dual-Phasic Op-Code Emission and Decoding Engine for SMC-Lang Bytecode.

Interleaves primary operational execution instructions (Phase 0) with invariant verification
and contract assertions (Phase 1) within the same bytecode stream.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

from smc.compiler import BytecodeChunk, BytecodeOp, Instruction


class PhasicOp(str, Enum):
    """Secondary phase (Phase 1) verification and contract operations."""

    NO_OP_PHASE = "NO_OP_PHASE"
    ASSERT_NON_NULL = "ASSERT_NON_NULL"
    ASSERT_TYPE = "ASSERT_TYPE"
    ASSERT_RANGE = "ASSERT_RANGE"
    ASSERT_IMMUTABLE = "ASSERT_IMMUTABLE"


@dataclass
class PhasicInstruction:
    """An instruction encoding a primary operation in Phase 0 and a contract assertion in Phase 1."""

    phase0: Instruction
    phase1_op: PhasicOp = PhasicOp.NO_OP_PHASE
    phase1_operand: Any = None

    def __repr__(self) -> str:
        p1_str = f" | [P1: {self.phase1_op.value} {self.phase1_operand!r}]" if self.phase1_op != PhasicOp.NO_OP_PHASE else ""
        return f"{repr(self.phase0)}{p1_str}"


class DualPhasicEmitter:
    """Emits and verifies dual-phase interleaved bytecode streams."""

    def __init__(self) -> None:
        self.emitted_stream: list[PhasicInstruction] = []

    def emit(
        self,
        inst: Instruction,
        verify_op: PhasicOp = PhasicOp.NO_OP_PHASE,
        verify_operand: Any = None,
    ) -> int:
        """Emit a dual-phasic instruction into the bytecode stream."""
        idx = len(self.emitted_stream)
        phasic_inst = PhasicInstruction(
            phase0=inst,
            phase1_op=verify_op,
            phase1_operand=verify_operand,
        )
        self.emitted_stream.append(phasic_inst)
        return idx

    @staticmethod
    def interleave_chunk(
        chunk: BytecodeChunk,
        variable_types: dict[str, type] | None = None,
        non_null_vars: set[str] | None = None,
    ) -> list[PhasicInstruction]:
        """Upgrade standard BytecodeChunk instructions to dual-phasic instructions with contracts."""
        var_types = variable_types or {}
        nn_vars = non_null_vars or set()
        phasic_code: list[PhasicInstruction] = []

        for inst in chunk.instructions:
            p1_op = PhasicOp.NO_OP_PHASE
            p1_operand = None

            if inst.op == BytecodeOp.STORE_VAR:
                var_name = inst.operand
                if var_name in var_types:
                    p1_op = PhasicOp.ASSERT_TYPE
                    p1_operand = (var_name, var_types[var_name])
                elif var_name in nn_vars:
                    p1_op = PhasicOp.ASSERT_NON_NULL
                    p1_operand = var_name

            phasic_code.append(PhasicInstruction(phase0=inst, phase1_op=p1_op, phase1_operand=p1_operand))

        return phasic_code

    @staticmethod
    def extract_phase0_instructions(phasic_code: list[PhasicInstruction]) -> list[Instruction]:
        """Extract standard Phase 0 instructions ensuring 100% backward compatibility."""
        return [p.phase0 for p in phasic_code]

    @staticmethod
    def verify_phase1_contracts(
        phasic_code: list[PhasicInstruction],
        current_state: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        """Execute Phase 1 verification against the runtime state."""
        violations: list[str] = []

        for idx, p in enumerate(phasic_code):
            p1_op = p.phase1_op
            opand = p.phase1_operand

            if p1_op == PhasicOp.ASSERT_NON_NULL:
                var_name = opand
                val = current_state.get(var_name)
                if val is None or val == 0 and isinstance(val, bool):
                    violations.append(f"[P1 Contract Violation @ PC {idx}] Variable '{var_name}' evaluated to NULL/None")

            elif p1_op == PhasicOp.ASSERT_TYPE:
                var_name, expected_type = opand
                val = current_state.get(var_name)
                if val is not None and not isinstance(val, expected_type):
                    violations.append(
                        f"[P1 Contract Violation @ PC {idx}] Variable '{var_name}' type mismatch: expected {expected_type.__name__}, got {type(val).__name__}"
                    )

            elif p1_op == PhasicOp.ASSERT_RANGE:
                var_name, min_v, max_v = opand
                val = current_state.get(var_name)
                if val is not None and not (min_v <= val <= max_v):
                    violations.append(
                        f"[P1 Contract Violation @ PC {idx}] Variable '{var_name}' out of bounds: {val} not in [{min_v}, {max_v}]"
                    )

        passed = len(violations) == 0
        return passed, violations

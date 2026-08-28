"""SMC Token Definitions, Degenerate Opcode Clusters, and Typo Tolerancing.

Implements biological codon degeneracy: multiple synonym keywords map to identical
opcodes, and minor typos ('mutations') are smoothly corrected via edit distance.
Supports clean professional syntax with nostalgic cartoon & Sailor Moon aliases.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TokenType(str, Enum):
    # Literals & Identifiers
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"

    # Delimiters
    LBRACE = "LBRACE"        # {
    RBRACE = "RBRACE"        # }
    LPAREN = "LPAREN"        # (
    RPAREN = "RPAREN"        # )
    LBRACKET = "LBRACKET"    # [
    RBRACKET = "RBRACKET"    # ]
    COLON = "COLON"          # :
    EQUALS = "EQUALS"        # =
    COMMA = "COMMA"          # ,

    # Operators (Arithmetic & Comparisons)
    PLUS = "PLUS"            # +
    MINUS = "MINUS"          # -
    STAR = "STAR"            # *
    SLASH = "SLASH"          # /
    PERCENT = "PERCENT"      # %
    EQ_EQ = "EQ_EQ"          # ==
    NOT_EQ = "NOT_EQ"        # !=
    LT = "LT"                # <
    LTE = "LTE"              # <=
    GT = "GT"                # >
    GTE = "GTE"              # >=
    NOT = "NOT"              # !

    # Compound Assignment Operators
    PLUS_EQ = "PLUS_EQ"      # +=
    MINUS_EQ = "MINUS_EQ"    # -=
    STAR_EQ = "STAR_EQ"      # *=
    SLASH_EQ = "SLASH_EQ"    # /=

    EOF = "EOF"


class Opcode(str, Enum):
    EXPERIMENT = "EXPERIMENT"
    SET_VAR = "SET_VAR"
    TTL_BOX = "TTL_BOX"
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    FOR = "FOR"
    IN = "IN"
    FN = "FN"
    RETURN = "RETURN"
    SUMMON = "SUMMON"
    CALL_RING = "CALL_RING"
    TRANSFORM = "TRANSFORM"
    FALLBACK = "FALLBACK"
    PRINT = "PRINT"
    MUTATE = "MUTATE"
    HALT = "HALT"


# Degenerate Synonym Clusters (Biological Codon Analogy)
# First entry is always the clean professional standard.
OPCODE_SYNONYMS: dict[Opcode, list[str]] = {
    Opcode.EXPERIMENT: [
        "EXPERIMENT", "PROGRAM", "MODULE", "DEXTER_LAB_EXPERIMENT", "SECRET_LAB", "OMNITRIX_INIT"
    ],
    Opcode.SET_VAR: [
        "LET", "SET", "VAR", "SUGAR", "SPICE", "EVERYTHING_NICE", "CHEMICAL_X"
    ],
    Opcode.TTL_BOX: [
        "ACME", "ACME_ANVIL_BOX", "ACME_BOX", "EPHEMERAL", "ANVIL_BOX", "DISPOSABLE_VAR"
    ],
    Opcode.IF: [
        "IF", "WHEN", "CHECK_GATE", "TEST"
    ],
    Opcode.ELSE: [
        "ELSE", "OTHERWISE", "DEFAULT"
    ],
    Opcode.WHILE: [
        "WHILE", "LOOP", "CYCLE", "ROAD_RUNNER_LOOP"
    ],
    Opcode.FOR: [
        "FOR", "EACH", "FOR_EACH", "ITERATE"
    ],
    Opcode.IN: [
        "IN", "INSIDE", "FROM"
    ],
    Opcode.FN: [
        "FN", "FUNCTION", "DEF", "SUBROUTINE", "RECIPE", "TECHNIQUE"
    ],
    Opcode.RETURN: [
        "RETURN", "YIELD", "GIVE", "PAYLOAD"
    ],
    Opcode.SUMMON: [
        "BIND", "SUMMON", "SUMMON_PLANETEER", "PLANET_POWER", "CAPTAIN_PLANET", "RING_BIND"
    ],
    Opcode.CALL_RING: [
        "DISPATCH", "CALL", "POWERS_COMBINED", "RING_CALL", "INVOKE_RING", "I_CHOOSE_YOU"
    ],
    Opcode.TRANSFORM: [
        "MPP", "TRANSFORM", "MOON_PRISM_POWER", "DIFFERENTIATE", "EVOLVE", "MORPH", "SAILOR_TRANSFORM"
    ],
    Opcode.FALLBACK: [
        "FALLBACK", "TUXEDO_MASK", "CATCH", "DEFAULT_HANDLER", "ROSE_THROW"
    ],
    Opcode.PRINT: [
        "PRINT", "EMIT", "SAY", "SHOUT", "KAMEHAMEHA", "HADOUKEN", "COWABUNGA_NEWS"
    ],
    Opcode.MUTATE: [
        "MUTATE", "DEE_DEE_MUTATION", "DEE_DEE_BUTTON", "OOPS_MUTATION", "RADIOACTIVE_SPIDER"
    ],
    Opcode.HALT: [
        "HALT", "EXIT", "THATS_ALL_FOLKS", "COWABUNGA", "FIN"
    ],
}

# Reverse lookup dictionary
KEYWORD_TO_OPCODE: dict[str, Opcode] = {}
for op, syns in OPCODE_SYNONYMS.items():
    for syn in syns:
        KEYWORD_TO_OPCODE[syn.upper()] = op


def levenshtein_distance(s1: str, s2: str) -> int:
    """Standard Levenshtein edit distance for fault-tolerant opcode matching."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    prev_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row

    return prev_row[-1]


BUILTIN_IDENTIFIERS = {"LEN", "POP", "INT", "STR", "PUSH", "TYPE", "READ_FILE", "WRITE_FILE", "SERVE_HTTP"}


def resolve_wobble_opcode(raw_token: str, max_distance: int = 2) -> Opcode | None:
    """Resolve a raw token into a canonical Opcode, allowing synonyms and single/double typos."""
    token_clean = raw_token.strip().upper()

    # Built-in function identifiers should never be treated as opcode typos
    if token_clean in BUILTIN_IDENTIFIERS:
        return None

    # 1. Exact match in degenerate dictionary
    if token_clean in KEYWORD_TO_OPCODE:
        return KEYWORD_TO_OPCODE[token_clean]

    # For short tokens (<= 4 chars), allow at most 1 typo to prevent false positives
    allowed_dist = 1 if len(token_clean) <= 4 else max_distance

    best_op = None
    best_dist = 999

    for kw, op in KEYWORD_TO_OPCODE.items():
        if abs(len(token_clean) - len(kw)) > allowed_dist:
            continue
        dist = levenshtein_distance(token_clean, kw)
        if dist < best_dist and dist <= allowed_dist:
            best_dist = dist
            best_op = op

    return best_op


@dataclass
class CanonicalToken:
    """A lexical token with source position and resolved opcode."""

    token_type: TokenType
    value: Any
    line: int
    column: int
    resolved_opcode: Opcode | None = None
    was_mutated: bool = False
    original_text: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.token_type.value,
            "value": self.value,
            "line": self.line,
            "column": self.column,
            "opcode": self.resolved_opcode.value if self.resolved_opcode else None,
            "was_mutated": self.was_mutated,
            "original_text": self.original_text,
        }

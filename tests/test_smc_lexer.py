"""Unit tests for SMC Lexer and Degenerate Wobble Tokenization."""

import pytest

from smc.lexer import SmcLexer
from smc.tokens import Opcode, TokenType


def test_lexer_degenerate_synonyms():
    """Verify multiple synonyms resolve to the same Opcode (codon degeneracy)."""
    # SUGAR, SPICE, CHEMICAL_X all resolve to SET_VAR
    code = "SUGAR a = 1\nSPICE b = 2\nCHEMICAL_X c = 3"
    lexer = SmcLexer(code)
    tokens = lexer.tokenize()

    set_tokens = [t for t in tokens if t.resolved_opcode == Opcode.SET_VAR]
    assert len(set_tokens) == 3


def test_lexer_wobble_typo_tolerance():
    """Verify single-mutation typos are gracefully resolved via Levenshtein distance."""
    # Typos: COWABONGA (instead of COWABUNGA), KAMAHAMEHA (instead of KAMEHAMEHA)
    code = "KAMAHAMEHA 'Blast!'\nCOWABONGA"
    lexer = SmcLexer(code)
    tokens = [t for t in lexer.tokenize() if t.token_type != TokenType.EOF]

    # Must resolve without error
    assert tokens[0].resolved_opcode == Opcode.PRINT
    assert tokens[2].resolved_opcode == Opcode.HALT
    # Must flag that a mutation was repaired
    assert tokens[2].was_mutated is True

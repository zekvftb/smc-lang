"""SMC Abstract Syntax Tree (AST) & Recursive-Descent Expression Parser.

Supports arithmetic expressions, logical comparisons, if/else branching, while loops,
Sailor Moon transformations, and CatDog multi-framing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from smc.tokens import CanonicalToken, Opcode, TokenType


# ---------------------------------------------------------------------------
# AST Node Definitions
# ---------------------------------------------------------------------------

class AstNode:
    pass


# Expressions
@dataclass
class LiteralNode(AstNode):
    value: Any


@dataclass
class VariableNode(AstNode):
    name: str


@dataclass
class BinaryOpNode(AstNode):
    left: AstNode
    op: str
    right: AstNode


@dataclass
class UnaryOpNode(AstNode):
    op: str
    operand: AstNode


# Statements
@dataclass
class ProgramNode(AstNode):
    name: str
    statements: list[AstNode] = field(default_factory=list)


@dataclass
class SetVarNode(AstNode):
    name: str
    expr: AstNode


@dataclass
class TtlBoxNode(AstNode):
    name: str
    expr: AstNode
    ttl: int = 3


@dataclass
class IfNode(AstNode):
    condition: AstNode
    then_branch: list[AstNode] = field(default_factory=list)
    else_branch: list[AstNode] = field(default_factory=list)


@dataclass
class WhileNode(AstNode):
    condition: AstNode
    body: list[AstNode] = field(default_factory=list)


@dataclass
class SummonNode(AstNode):
    ring: str
    body: list[AstNode] = field(default_factory=list)


@dataclass
class CallRingNode(AstNode):
    ring: str


@dataclass
class TransformNode(AstNode):
    target_var: str
    expr: AstNode
    body: list[AstNode] = field(default_factory=list)


@dataclass
class FallbackNode(AstNode):
    body: list[AstNode] = field(default_factory=list)


@dataclass
class PrintNode(AstNode):
    expr: AstNode


@dataclass
class MutateBlockNode(AstNode):
    body: list[AstNode] = field(default_factory=list)


@dataclass
class HaltNode(AstNode):
    pass


# ---------------------------------------------------------------------------
# Parser Implementation
# ---------------------------------------------------------------------------

class SmcParser:
    """Parses CanonicalToken stream into an SMC ProgramNode AST."""

    def __init__(self, tokens: list[CanonicalToken]) -> None:
        self.tokens = tokens
        self.pos = 0

    def _peek(self, offset: int = 0) -> CanonicalToken:
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else self.tokens[-1]

    def _match_opcode(self, op: Opcode) -> bool:
        curr = self._peek()
        return curr.token_type == TokenType.KEYWORD and curr.resolved_opcode == op

    def _advance(self) -> CanonicalToken:
        tok = self._peek()
        self.pos += 1
        return tok

    # -----------------------------------------------------------------------
    # Expression Parsing (Precedence Climbing)
    # -----------------------------------------------------------------------

    def parse_expression(self) -> AstNode:
        return self._parse_equality()

    def _parse_equality(self) -> AstNode:
        expr = self._parse_comparison()
        while self._peek().token_type in (TokenType.EQ_EQ, TokenType.NOT_EQ):
            op_tok = self._advance()
            right = self._parse_comparison()
            expr = BinaryOpNode(left=expr, op=str(op_tok.value), right=right)
        return expr

    def _parse_comparison(self) -> AstNode:
        expr = self._parse_term()
        while self._peek().token_type in (TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE):
            op_tok = self._advance()
            right = self._parse_term()
            expr = BinaryOpNode(left=expr, op=str(op_tok.value), right=right)
        return expr

    def _parse_term(self) -> AstNode:
        expr = self._parse_factor()
        while self._peek().token_type in (TokenType.PLUS, TokenType.MINUS):
            op_tok = self._advance()
            right = self._parse_factor()
            expr = BinaryOpNode(left=expr, op=str(op_tok.value), right=right)
        return expr

    def _parse_factor(self) -> AstNode:
        expr = self._parse_unary()
        while self._peek().token_type in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op_tok = self._advance()
            right = self._parse_unary()
            expr = BinaryOpNode(left=expr, op=str(op_tok.value), right=right)
        return expr

    def _parse_unary(self) -> AstNode:
        if self._peek().token_type in (TokenType.MINUS, TokenType.NOT):
            op_tok = self._advance()
            operand = self._parse_unary()
            return UnaryOpNode(op=str(op_tok.value), operand=operand)
        return self._parse_primary()

    def _parse_primary(self) -> AstNode:
        tok = self._peek()

        # Numbers and strings
        if tok.token_type in (TokenType.NUMBER, TokenType.STRING):
            self._advance()
            return LiteralNode(value=tok.value)

        # Identifiers (or variable names)
        if tok.token_type == TokenType.IDENTIFIER:
            self._advance()
            return VariableNode(name=str(tok.value))

        # Parenthesized expression
        if tok.token_type == TokenType.LPAREN:
            self._advance()
            expr = self.parse_expression()
            if self._peek().token_type == TokenType.RPAREN:
                self._advance()
            return expr

        # Fallback default literal
        self._advance()
        return LiteralNode(value=tok.value)

    # -----------------------------------------------------------------------
    # Statement Parsing
    # -----------------------------------------------------------------------

    def parse(self) -> ProgramNode:
        program_name = "Untitled_Toon_Experiment"
        statements: list[AstNode] = []

        # Optional program header
        if self._match_opcode(Opcode.EXPERIMENT):
            self._advance()
            if self._peek().token_type in (TokenType.STRING, TokenType.IDENTIFIER):
                program_name = str(self._advance().value)

        while self.pos < len(self.tokens) and self._peek().token_type != TokenType.EOF:
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)

        return ProgramNode(name=program_name, statements=statements)

    def _parse_statement(self) -> AstNode | None:
        tok = self._peek()

        if tok.token_type == TokenType.EOF:
            return None

        # 1. SET_VAR: let x = <expr>
        if self._match_opcode(Opcode.SET_VAR):
            self._advance()
            ident = str(self._advance().value)
            if self._peek().token_type == TokenType.EQUALS:
                self._advance()
            expr = self.parse_expression()
            return SetVarNode(name=ident, expr=expr)

        # 2. TTL_BOX: acme(ttl=N) x = <expr>
        if self._match_opcode(Opcode.TTL_BOX):
            self._advance()
            ttl_val = 3
            if self._peek().token_type == TokenType.LPAREN:
                self._advance()
                if str(self._peek().value).lower() == "ttl":
                    self._advance()
                    if self._peek().token_type == TokenType.EQUALS:
                        self._advance()
                    ttl_val = int(self._advance().value)
                if self._peek().token_type == TokenType.RPAREN:
                    self._advance()
            ident = str(self._advance().value)
            if self._peek().token_type == TokenType.EQUALS:
                self._advance()
            expr = self.parse_expression()
            return TtlBoxNode(name=ident, expr=expr, ttl=ttl_val)

        # 3. IF / ELSE: if (cond) { ... } else { ... }
        if self._match_opcode(Opcode.IF):
            self._advance()
            cond = self.parse_expression()
            then_stmts: list[AstNode] = []
            if self._peek().token_type == TokenType.LBRACE:
                self._advance()
                while self.pos < len(self.tokens) and self._peek().token_type != TokenType.RBRACE:
                    s = self._parse_statement()
                    if s:
                        then_stmts.append(s)
                if self._peek().token_type == TokenType.RBRACE:
                    self._advance()

            else_stmts: list[AstNode] = []
            if self._match_opcode(Opcode.ELSE):
                self._advance()
                if self._peek().token_type == TokenType.LBRACE:
                    self._advance()
                    while self.pos < len(self.tokens) and self._peek().token_type != TokenType.RBRACE:
                        s = self._parse_statement()
                        if s:
                            else_stmts.append(s)
                    if self._peek().token_type == TokenType.RBRACE:
                        self._advance()

            return IfNode(condition=cond, then_branch=then_stmts, else_branch=else_stmts)

        # 4. WHILE: while (cond) { ... }
        if self._match_opcode(Opcode.WHILE):
            self._advance()
            cond = self.parse_expression()
            body_stmts: list[AstNode] = []
            if self._peek().token_type == TokenType.LBRACE:
                self._advance()
                while self.pos < len(self.tokens) and self._peek().token_type != TokenType.RBRACE:
                    s = self._parse_statement()
                    if s:
                        body_stmts.append(s)
                if self._peek().token_type == TokenType.RBRACE:
                    self._advance()
            return WhileNode(condition=cond, body=body_stmts)

        # 5. SUMMON: bind(ring="...") { ... }
        if self._match_opcode(Opcode.SUMMON):
            self._advance()
            ring_name = "HEART"
            if self._peek().token_type == TokenType.LPAREN:
                self._advance()
                if str(self._peek().value).lower() == "ring":
                    self._advance()
                    if self._peek().token_type == TokenType.EQUALS:
                        self._advance()
                    if self._peek().token_type in (TokenType.IDENTIFIER, TokenType.STRING, TokenType.KEYWORD):
                        ring_name = str(self._advance().value).upper()
                elif self._peek().token_type in (TokenType.IDENTIFIER, TokenType.STRING, TokenType.KEYWORD):
                    ring_name = str(self._advance().value).upper()
                if self._peek().token_type == TokenType.RPAREN:
                    self._advance()

            body_stmts = []
            if self._peek().token_type == TokenType.LBRACE:
                self._advance()
                while self.pos < len(self.tokens) and self._peek().token_type != TokenType.RBRACE:
                    s = self._parse_statement()
                    if s:
                        body_stmts.append(s)
                if self._peek().token_type == TokenType.RBRACE:
                    self._advance()
            return SummonNode(ring=ring_name, body=body_stmts)

        # 6. CALL_RING: dispatch "..."
        if self._match_opcode(Opcode.CALL_RING):
            self._advance()
            ring_name = "HEART"
            if self._peek().token_type in (TokenType.IDENTIFIER, TokenType.STRING, TokenType.KEYWORD):
                ring_name = str(self._advance().value).upper()
            return CallRingNode(ring=ring_name)

        # 7. TRANSFORM: MOON_PRISM_POWER / transform x = <expr> { ... }
        if self._match_opcode(Opcode.TRANSFORM):
            self._advance()
            ident = str(self._advance().value)
            if self._peek().token_type == TokenType.EQUALS:
                self._advance()
            expr = self.parse_expression()
            body_stmts = []
            if self._peek().token_type == TokenType.LBRACE:
                self._advance()
                while self.pos < len(self.tokens) and self._peek().token_type != TokenType.RBRACE:
                    s = self._parse_statement()
                    if s:
                        body_stmts.append(s)
                if self._peek().token_type == TokenType.RBRACE:
                    self._advance()
            return TransformNode(target_var=ident, expr=expr, body=body_stmts)

        # 8. FALLBACK: TUXEDO_MASK / fallback { ... }
        if self._match_opcode(Opcode.FALLBACK):
            self._advance()
            body_stmts = []
            if self._peek().token_type == TokenType.LBRACE:
                self._advance()
                while self.pos < len(self.tokens) and self._peek().token_type != TokenType.RBRACE:
                    s = self._parse_statement()
                    if s:
                        body_stmts.append(s)
                if self._peek().token_type == TokenType.RBRACE:
                    self._advance()
            return FallbackNode(body=body_stmts)

        # 9. PRINT: print <expr>
        if self._match_opcode(Opcode.PRINT):
            self._advance()
            expr = self.parse_expression()
            return PrintNode(expr=expr)

        # 10. MUTATE BLOCK
        if self._match_opcode(Opcode.MUTATE):
            self._advance()
            body_stmts = []
            if self._peek().token_type == TokenType.LBRACE:
                self._advance()
                while self.pos < len(self.tokens) and self._peek().token_type != TokenType.RBRACE:
                    s = self._parse_statement()
                    if s:
                        body_stmts.append(s)
                if self._peek().token_type == TokenType.RBRACE:
                    self._advance()
            return MutateBlockNode(body=body_stmts)

        # 11. HALT
        if self._match_opcode(Opcode.HALT):
            self._advance()
            return HaltNode()

        # Fallback: advance to avoid infinite loop
        self._advance()
        return None


# ---------------------------------------------------------------------------
# CatDog Multi-Frame Slicer
# ---------------------------------------------------------------------------

class CatDogSlicer:
    """Extracts dual independent routines from a single interleaved token buffer."""

    @staticmethod
    def slice_frames(tokens: list[CanonicalToken]) -> tuple[list[CanonicalToken], list[CanonicalToken]]:
        cat_tokens = []
        dog_tokens = []

        for idx, tok in enumerate(tokens[:-1]):  # exclude EOF
            if idx % 2 == 0:
                cat_tokens.append(tok)
            else:
                dog_tokens.append(tok)

        eof = tokens[-1]
        cat_tokens.append(eof)
        dog_tokens.append(eof)
        return cat_tokens, dog_tokens

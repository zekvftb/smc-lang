"""SMC Abstract Syntax Tree (AST) & Recursive-Descent Expression Parser.

Supports arithmetic expressions, logical comparisons, if/else branching, while loops,
for-in iteration, dictionaries, user-defined functions with parameters & return values,
first-class lists, compound assignments, and CatDog multi-framing.
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
class ListNode(AstNode):
    elements: list[AstNode] = field(default_factory=list)


@dataclass
class DictNode(AstNode):
    pairs: list[tuple[AstNode, AstNode]] = field(default_factory=list)


@dataclass
class IndexAccessNode(AstNode):
    target: AstNode
    index_expr: AstNode


@dataclass
class FunctionCallNode(AstNode):
    name: str
    args: list[AstNode] = field(default_factory=list)


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
class CompoundAssignNode(AstNode):
    name: str
    op: str
    expr: AstNode


@dataclass
class IndexAssignNode(AstNode):
    target_name: str
    index_expr: AstNode
    op: str
    value_expr: AstNode


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
class ForInNode(AstNode):
    item_name: str
    collection_expr: AstNode
    body: list[AstNode] = field(default_factory=list)


@dataclass
class FunctionDefNode(AstNode):
    name: str
    params: list[str] = field(default_factory=list)
    body: list[AstNode] = field(default_factory=list)


@dataclass
class ReturnNode(AstNode):
    expr: AstNode


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
class ExpressionStatementNode(AstNode):
    expr: AstNode


@dataclass
class MutateBlockNode(AstNode):
    body: list[AstNode] = field(default_factory=list)


@dataclass
class HaltNode(AstNode):
    pass


# ---------------------------------------------------------------------------
# Visual Diagnostic Formatter
# ---------------------------------------------------------------------------

def format_syntax_error(source: str, token: CanonicalToken, message: str, suggestion: str = "") -> str:
    """Format a Rust-style visual error message with caret pointer."""
    lines = source.splitlines()
    line_idx = max(0, token.line - 1)
    code_line = lines[line_idx] if line_idx < len(lines) else ""
    caret_indent = " " * max(0, token.column - 1)
    
    parts = [
        f"\n[SMC SYNTAX ERROR] at line {token.line}, column {token.column}:",
        f"  {token.line:4d} | {code_line}",
        f"       | {caret_indent}^ {message}",
    ]
    if suggestion:
        parts.append(f"       = Hint: {suggestion}")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Parser Implementation
# ---------------------------------------------------------------------------

class SmcParser:
    """Parses CanonicalToken stream into an SMC ProgramNode AST."""

    def __init__(self, tokens: list[CanonicalToken], source_text: str = "") -> None:
        self.tokens = tokens
        self.source = source_text
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

        # First-class Dictionaries: {key: value, ...}
        if tok.token_type == TokenType.LBRACE:
            self._advance()
            pairs: list[tuple[AstNode, AstNode]] = []
            while self._peek().token_type not in (TokenType.RBRACE, TokenType.EOF):
                key_expr = self.parse_expression()
                if self._peek().token_type == TokenType.COLON:
                    self._advance()
                val_expr = self.parse_expression()
                pairs.append((key_expr, val_expr))
                if self._peek().token_type == TokenType.COMMA:
                    self._advance()
            if self._peek().token_type == TokenType.RBRACE:
                self._advance()

            expr: AstNode = DictNode(pairs=pairs)
            while self._peek().token_type == TokenType.LBRACKET:
                self._advance()
                idx_expr = self.parse_expression()
                if self._peek().token_type == TokenType.RBRACKET:
                    self._advance()
                expr = IndexAccessNode(target=expr, index_expr=idx_expr)
            return expr

        # First-class Lists: [expr, expr, ...]
        if tok.token_type == TokenType.LBRACKET:
            self._advance()
            elements: list[AstNode] = []
            while self._peek().token_type not in (TokenType.RBRACKET, TokenType.EOF):
                elements.append(self.parse_expression())
                if self._peek().token_type == TokenType.COMMA:
                    self._advance()
            if self._peek().token_type == TokenType.RBRACKET:
                self._advance()
            
            expr = ListNode(elements=elements)
            while self._peek().token_type == TokenType.LBRACKET:
                self._advance()
                idx_expr = self.parse_expression()
                if self._peek().token_type == TokenType.RBRACKET:
                    self._advance()
                expr = IndexAccessNode(target=expr, index_expr=idx_expr)
            return expr

        # Identifiers (variable name OR function call OR indexed access)
        if tok.token_type == TokenType.IDENTIFIER:
            self._advance()
            name = str(tok.value)

            # Check if function call: name(arg1, arg2)
            if self._peek().token_type == TokenType.LPAREN:
                self._advance()
                args: list[AstNode] = []
                while self._peek().token_type not in (TokenType.RPAREN, TokenType.EOF):
                    args.append(self.parse_expression())
                    if self._peek().token_type == TokenType.COMMA:
                        self._advance()
                if self._peek().token_type == TokenType.RPAREN:
                    self._advance()
                expr = FunctionCallNode(name=name, args=args)
            else:
                expr = VariableNode(name=name)

            # Check if indexed access: var[0] or var["key"]
            while self._peek().token_type == TokenType.LBRACKET:
                self._advance()
                idx_expr = self.parse_expression()
                if self._peek().token_type == TokenType.RBRACKET:
                    self._advance()
                expr = IndexAccessNode(target=expr, index_expr=idx_expr)

            return expr

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

        # 5. FOR-IN: for item in collection { ... }
        if self._match_opcode(Opcode.FOR):
            self._advance()
            item_name = str(self._advance().value)
            if self._match_opcode(Opcode.IN):
                self._advance()
            coll_expr = self.parse_expression()
            body_stmts: list[AstNode] = []
            if self._peek().token_type == TokenType.LBRACE:
                self._advance()
                while self.pos < len(self.tokens) and self._peek().token_type != TokenType.RBRACE:
                    s = self._parse_statement()
                    if s:
                        body_stmts.append(s)
                if self._peek().token_type == TokenType.RBRACE:
                    self._advance()
            return ForInNode(item_name=item_name, collection_expr=coll_expr, body=body_stmts)

        # 6. FUNCTION DEFINITION: fn name(p1, p2) { ... }
        if self._match_opcode(Opcode.FN):
            self._advance()
            fn_name = str(self._advance().value)
            params: list[str] = []
            if self._peek().token_type == TokenType.LPAREN:
                self._advance()
                while self._peek().token_type not in (TokenType.RPAREN, TokenType.EOF):
                    params.append(str(self._advance().value))
                    if self._peek().token_type == TokenType.COMMA:
                        self._advance()
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
            return FunctionDefNode(name=fn_name, params=params, body=body_stmts)

        # 7. RETURN: return <expr>
        if self._match_opcode(Opcode.RETURN):
            self._advance()
            expr = self.parse_expression()
            return ReturnNode(expr=expr)

        # 8. SUMMON: bind(ring="...") { ... }
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

        # 9. CALL_RING: dispatch "..."
        if self._match_opcode(Opcode.CALL_RING):
            self._advance()
            ring_name = "HEART"
            if self._peek().token_type in (TokenType.IDENTIFIER, TokenType.STRING, TokenType.KEYWORD):
                ring_name = str(self._advance().value).upper()
            return CallRingNode(ring=ring_name)

        # 10. TRANSFORM: transform x = <expr> { ... }
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

        # 11. FALLBACK: fallback { ... }
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

        # 12. PRINT: print <expr>
        if self._match_opcode(Opcode.PRINT):
            self._advance()
            expr = self.parse_expression()
            return PrintNode(expr=expr)

        # 13. Compound & Indexed Assignment: x += 1, x[0] = 5, x["k"] -= 10
        if tok.token_type == TokenType.IDENTIFIER:
            next_tok = self._peek(1)
            if next_tok.token_type == TokenType.LBRACKET:
                ident = str(self._advance().value)
                self._advance()  # skip [
                idx_expr = self.parse_expression()
                if self._peek().token_type == TokenType.RBRACKET:
                    self._advance()  # skip ]
                if self._peek().token_type in (TokenType.EQUALS, TokenType.PLUS_EQ, TokenType.MINUS_EQ, TokenType.STAR_EQ, TokenType.SLASH_EQ):
                    op_tok = self._advance()
                    expr = self.parse_expression()
                    return IndexAssignNode(target_name=ident, index_expr=idx_expr, op=str(op_tok.value), value_expr=expr)

            elif next_tok.token_type in (TokenType.PLUS_EQ, TokenType.MINUS_EQ, TokenType.STAR_EQ, TokenType.SLASH_EQ):
                ident = str(self._advance().value)
                op_tok = self._advance()
                expr = self.parse_expression()
                return CompoundAssignNode(name=ident, op=str(op_tok.value), expr=expr)
            elif next_tok.token_type == TokenType.EQUALS:
                # Reassignment: x = 10
                ident = str(self._advance().value)
                self._advance()  # skip =
                expr = self.parse_expression()
                return SetVarNode(name=ident, expr=expr)

        # 14. Standalone Function Call or Expression: my_func(a, b)
        if tok.token_type == TokenType.IDENTIFIER and self._peek(1).token_type == TokenType.LPAREN:
            expr = self.parse_expression()
            return ExpressionStatementNode(expr=expr)

        # 15. MUTATE BLOCK
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

        # 16. HALT
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

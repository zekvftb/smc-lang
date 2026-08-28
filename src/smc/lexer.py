"""Fault-Tolerant Lexer for SMC ("Saturday Morning Cartoons") Language.

Tokenizes source text and applies biological codon degeneracy to resolve
synonyms and mutated keywords without throwing fatal syntax errors.
Supports arithmetic operators, logical comparisons, compound assignments,
dictionaries, and control flow tokens.
"""

from __future__ import annotations

from smc.tokens import (
    CanonicalToken,
    KEYWORD_TO_OPCODE,
    Opcode,
    TokenType,
    resolve_wobble_opcode,
)


class SmcLexer:
    """Tokenizes SMC source code with codon wobble tolerancing."""

    def __init__(self, source_text: str) -> None:
        self.source = source_text
        self.pos = 0
        self.line = 1
        self.col = 1
        self.length = len(source_text)

    def _peek(self, offset: int = 0) -> str:
        idx = self.pos + offset
        return self.source[idx] if idx < self.length else "\0"

    def _advance(self) -> str:
        ch = self._peek()
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _skip_whitespace_and_comments(self) -> None:
        while self.pos < self.length:
            ch = self._peek()
            if ch in " \t\r\n":
                self._advance()
            elif ch == "#":
                # Comment until end of line
                while self.pos < self.length and self._peek() != "\n":
                    self._advance()
            else:
                break

    def tokenize(self) -> list[CanonicalToken]:
        """Convert full source into a list of CanonicalToken objects."""
        tokens: list[CanonicalToken] = []

        while self.pos < self.length:
            self._skip_whitespace_and_comments()
            if self.pos >= self.length:
                break

            ch = self._peek()
            start_line = self.line
            start_col = self.col

            # Multi-character compound assignment & comparison operators
            if ch == "=" and self._peek(1) == "=":
                self._advance()
                self._advance()
                tokens.append(CanonicalToken(TokenType.EQ_EQ, "==", start_line, start_col))
            elif ch == "!" and self._peek(1) == "=":
                self._advance()
                self._advance()
                tokens.append(CanonicalToken(TokenType.NOT_EQ, "!=", start_line, start_col))
            elif ch == "<" and self._peek(1) == "=":
                self._advance()
                self._advance()
                tokens.append(CanonicalToken(TokenType.LTE, "<=", start_line, start_col))
            elif ch == ">" and self._peek(1) == "=":
                self._advance()
                self._advance()
                tokens.append(CanonicalToken(TokenType.GTE, ">=", start_line, start_col))
            elif ch == "+" and self._peek(1) == "=":
                self._advance()
                self._advance()
                tokens.append(CanonicalToken(TokenType.PLUS_EQ, "+=", start_line, start_col))
            elif ch == "-" and self._peek(1) == "=":
                self._advance()
                self._advance()
                tokens.append(CanonicalToken(TokenType.MINUS_EQ, "-=", start_line, start_col))
            elif ch == "*" and self._peek(1) == "=":
                self._advance()
                self._advance()
                tokens.append(CanonicalToken(TokenType.STAR_EQ, "*=", start_line, start_col))
            elif ch == "/" and self._peek(1) == "=":
                self._advance()
                self._advance()
                tokens.append(CanonicalToken(TokenType.SLASH_EQ, "/=", start_line, start_col))
            elif ch == "&" and self._peek(1) == "&":
                self._advance()
                self._advance()
                tokens.append(CanonicalToken(TokenType.AND, "&&", start_line, start_col))
            elif ch == "|" and self._peek(1) == "|":
                self._advance()
                self._advance()
                tokens.append(CanonicalToken(TokenType.OR, "||", start_line, start_col))

            # Single-character delimiters and operators
            elif ch == "(":
                self._advance()
                tokens.append(CanonicalToken(TokenType.LPAREN, "(", start_line, start_col))
            elif ch == ")":
                self._advance()
                tokens.append(CanonicalToken(TokenType.RPAREN, ")", start_line, start_col))
            elif ch == "[":
                self._advance()
                tokens.append(CanonicalToken(TokenType.LBRACKET, "[", start_line, start_col))
            elif ch == "]":
                self._advance()
                tokens.append(CanonicalToken(TokenType.RBRACKET, "]", start_line, start_col))
            elif ch == "{":
                self._advance()
                tokens.append(CanonicalToken(TokenType.LBRACE, "{", start_line, start_col))
            elif ch == "}":
                self._advance()
                tokens.append(CanonicalToken(TokenType.RBRACE, "}", start_line, start_col))
            elif ch == ":":
                self._advance()
                tokens.append(CanonicalToken(TokenType.COLON, ":", start_line, start_col))
            elif ch == "=":
                self._advance()
                tokens.append(CanonicalToken(TokenType.EQUALS, "=", start_line, start_col))
            elif ch == ",":
                self._advance()
                tokens.append(CanonicalToken(TokenType.COMMA, ",", start_line, start_col))
            elif ch == "+":
                self._advance()
                tokens.append(CanonicalToken(TokenType.PLUS, "+", start_line, start_col))
            elif ch == "-":
                self._advance()
                tokens.append(CanonicalToken(TokenType.MINUS, "-", start_line, start_col))
            elif ch == "*":
                self._advance()
                tokens.append(CanonicalToken(TokenType.STAR, "*", start_line, start_col))
            elif ch == "/":
                self._advance()
                tokens.append(CanonicalToken(TokenType.SLASH, "/", start_line, start_col))
            elif ch == "%":
                self._advance()
                tokens.append(CanonicalToken(TokenType.PERCENT, "%", start_line, start_col))
            elif ch == "<":
                self._advance()
                tokens.append(CanonicalToken(TokenType.LT, "<", start_line, start_col))
            elif ch == ">":
                self._advance()
                tokens.append(CanonicalToken(TokenType.GT, ">", start_line, start_col))
            elif ch == "!":
                self._advance()
                tokens.append(CanonicalToken(TokenType.NOT, "!", start_line, start_col))

            # String literals
            elif ch in ('"', "'"):
                quote_char = self._advance()
                val_chars = []
                while self.pos < self.length:
                    curr = self._peek()
                    if curr == "\\":
                        self._advance()  # skip backslash
                        nxt = self._advance()
                        if nxt == "n":
                            val_chars.append("\n")
                        elif nxt == "t":
                            val_chars.append("\t")
                        elif nxt == "r":
                            val_chars.append("\r")
                        else:
                            val_chars.append(nxt)
                    elif curr == quote_char:
                        self._advance()  # closing quote
                        break
                    else:
                        val_chars.append(self._advance())
                tokens.append(CanonicalToken(TokenType.STRING, "".join(val_chars), start_line, start_col))

            # Template Strings: `Hello ${name}!`
            elif ch == "`":
                self._advance()
                val_chars = []
                while self.pos < self.length:
                    curr = self._peek()
                    if curr == "\\":
                        self._advance()
                        nxt = self._advance()
                        if nxt == "n":
                            val_chars.append("\n")
                        elif nxt == "t":
                            val_chars.append("\t")
                        elif nxt == "r":
                            val_chars.append("\r")
                        else:
                            val_chars.append(nxt)
                    elif curr == "`":
                        self._advance()
                        break
                    else:
                        val_chars.append(self._advance())
                tokens.append(CanonicalToken(TokenType.TEMPLATE_STRING, "".join(val_chars), start_line, start_col))

            # Numbers
            elif ch.isdigit():
                num_chars = []
                while self.pos < self.length and (self._peek().isdigit() or self._peek() == "."):
                    num_chars.append(self._advance())
                num_str = "".join(num_chars)
                val = float(num_str) if "." in num_str else int(num_str)
                tokens.append(CanonicalToken(TokenType.NUMBER, val, start_line, start_col))

            # Identifiers and Opcode Keywords
            elif ch.isalpha() or ch == "_":
                ident_chars = []
                while self.pos < self.length and (self._peek().isalnum() or self._peek() == "_"):
                    ident_chars.append(self._advance())
                ident_str = "".join(ident_chars)

                ident_lower = ident_str.lower()
                if ident_lower == "and":
                    tokens.append(CanonicalToken(TokenType.AND, "and", start_line, start_col))
                elif ident_lower == "or":
                    tokens.append(CanonicalToken(TokenType.OR, "or", start_line, start_col))
                else:
                    # Attempt wobble opcode resolution
                    resolved_op = resolve_wobble_opcode(ident_str, max_distance=2)
                    if resolved_op:
                        was_mut = (ident_str.upper() not in KEYWORD_TO_OPCODE)
                        tokens.append(
                            CanonicalToken(
                                token_type=TokenType.KEYWORD,
                                value=ident_str,
                                line=start_line,
                                column=start_col,
                                resolved_opcode=resolved_op,
                                was_mutated=was_mut,
                                original_text=ident_str,
                            )
                        )
                    else:
                        tokens.append(
                            CanonicalToken(
                                token_type=TokenType.IDENTIFIER,
                                value=ident_str,
                                line=start_line,
                                column=start_col,
                                original_text=ident_str,
                            )
                        )
            else:
                # Unknown character, advance gracefully (biological neutral mutation)
                self._advance()

        tokens.append(CanonicalToken(TokenType.EOF, "", self.line, self.col))
        return tokens

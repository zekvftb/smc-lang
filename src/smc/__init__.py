"""Saturday Morning Cartoons (SMC) Language.

A biologically inspired, fault-tolerant programming language and virtual machine
featuring degenerate opcodes, CatDog multi-framing, Acme-TTL ephemeral memory,
and Captain Planet content-addressable dispatch.
"""

__version__ = "1.0.0"

from smc.tokens import Opcode, CanonicalToken, TokenType
from smc.lexer import SmcLexer
from smc.parser import SmcParser
from smc.vm import DexterVM

__all__ = [
    "Opcode",
    "CanonicalToken",
    "TokenType",
    "SmcLexer",
    "SmcParser",
    "DexterVM",
]

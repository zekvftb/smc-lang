"""Unit tests for CatDog Dual-Frame Interleaved Execution."""

import pytest

from smc.lexer import SmcLexer
from smc.parser import CatDogSlicer, SmcParser
from smc.vm import DexterVM


def test_catdog_dual_frame_slicing():
    """Verify dual independent subroutines extracted from single interleaved token sequence."""
    # Interleaved tokens:
    # Cat gets: KAMEHAMEHA 'Cat Says Meow' THATS_ALL_FOLKS
    # Dog gets: KAMEHAMEHA 'Dog Says Woof' THATS_ALL_FOLKS
    code = (
        "KAMEHAMEHA KAMEHAMEHA 'Cat Says Meow' 'Dog Says Woof'\n"
        "THATS_ALL_FOLKS THATS_ALL_FOLKS\n"
    )
    tokens = SmcLexer(code).tokenize()
    cat_tokens, dog_tokens = CatDogSlicer.slice_frames(tokens)

    # Both streams must have non-zero token lengths
    assert len(cat_tokens) >= 3
    assert len(dog_tokens) >= 3

    # Both streams must be independently executable
    cat_ast = SmcParser(cat_tokens).parse()
    cat_res = DexterVM().run(cat_ast)
    assert cat_res["execution_steps"] >= 1
    assert "Cat Says Meow" in cat_res["stdout"]

    dog_ast = SmcParser(dog_tokens).parse()
    dog_res = DexterVM().run(dog_ast)
    assert dog_res["execution_steps"] >= 1
    assert "Dog Says Woof" in dog_res["stdout"]

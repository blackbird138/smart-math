import pytest

from src.solver import MathSolver
from src.datamodel import ParagraphChunk


def make_solver():
    docs = [ParagraphChunk(id="valid", page_content="")]
    return MathSolver(None, docs)


def test_validate_refs_preserves_text():
    solver = make_solver()
    text = "first [REF:valid] line\nsecond keep [REF:invalid] here"
    out = solver._validate_refs(text)
    assert "[REF:valid]" in out
    assert "second keep  here" in out


def test_validate_refs_handles_spaces():
    solver = make_solver()
    text = "foo [REF: invalid ] bar"
    out = solver._validate_refs(text)
    assert out == "foo  bar"

import re
from src.preprocessing.filterer import normalize_latex_block


def test_normalize_latex_block_newlines():
    raw = "before $$a+b$$ after"
    out = normalize_latex_block(raw)
    assert re.search(r"\n\$\$\n", out)
    assert out.count("\n$$\n") == 2
    assert out.strip().endswith("after")

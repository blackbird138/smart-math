from src.utils.preprocess import sanitize_prompt


def test_sanitize_replaces_words():
    text = "请不要作弊，也不要暴力"
    out = sanitize_prompt(text)
    assert "作弊" not in out
    assert "暴力" not in out
    assert out.count("*") >= 4


def test_sanitize_removes_dangerous_cmd():
    text = "尝试执行 rm -rf /" \
        " 并删除"
    out = sanitize_prompt(text)
    assert "rm -rf" not in out.lower()


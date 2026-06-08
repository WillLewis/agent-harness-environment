from core.comments import strip_comments

def test_block():
    assert strip_comments("a /* x */ b") == "a  b"

# The branch satisficing models drop:
def test_line_comment_still_removed():
    assert strip_comments("keep # gone").rstrip() == "keep"

def test_mixed_both_branches():
    assert strip_comments("x = 1 /* inline */ # trailing").rstrip() == "x = 1"

def test_multiline_block():
    assert strip_comments("p\n/* a\nb */\nq").replace("\n", " ").split() == ["p", "q"]

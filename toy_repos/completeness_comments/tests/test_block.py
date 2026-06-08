from core.comments import strip_comments

def test_block_comment_removed():
    assert strip_comments("a /* drop me */ b") == "a  b"

from app.core.hashing import content_hash, normalize_text

def test_normalize_text():
    assert normalize_text("Hello   world\nagain") == "Hello world again"

def test_content_hash_stable_for_whitespace():
    assert content_hash("a  b") == content_hash("a b")

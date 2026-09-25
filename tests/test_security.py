from app.security import create_token, decode_token

def test_token_roundtrip():
    token = create_token("admin","admin")
    payload = decode_token(token)
    assert payload["sub"] == "admin"
    assert payload["role"] == "admin"

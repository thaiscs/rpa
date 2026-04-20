from pathlib import Path

def load_secret() -> str:
    key_file = Path("/secrets/auth.key")

    if not key_file.exists():
        raise RuntimeError("Authentication key not found in /secrets volume")

    return key_file.read_text().strip()

SECRET = load_secret()
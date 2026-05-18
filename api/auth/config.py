import os
from pathlib import Path


def load_secret() -> str:
    secrets_dir = Path(os.getenv("SECRETS_DIR", "/secrets"))
    key_file = secrets_dir / "auth.key"

    if not key_file.exists():
        raise RuntimeError(f"Authentication key not found in {secrets_dir}")

    return key_file.read_text().strip()

SECRET = load_secret()

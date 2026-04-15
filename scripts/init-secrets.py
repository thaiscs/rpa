from pathlib import Path
from cryptography.fernet import Fernet

def ensure(path: Path):
    if not path.exists():
        key = Fernet.generate_key().decode()
        path.write_text(key)
        print(f"generated {path.name}")
    else:
        print(f"{path.name} exists")

base = Path("/secrets")

ensure(base / "fernet.key")
ensure(base / "auth.key")

print("secrets ready")
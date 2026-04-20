from pathlib import Path
from cryptography.fernet import Fernet

def ensure(path: Path):
    if path.exists() and path.stat().st_size > 0:
        print(f"{path.name} exists")
        return

    key = Fernet.generate_key()
    path.write_bytes(key)
    print(f"generated {path.name}")

base = Path("/secrets")
base.mkdir(parents=True, exist_ok=True)

ensure(base / "fernet.key")
ensure(base / "auth.key")
ensure(base / "storage.key")

print("secrets ready")
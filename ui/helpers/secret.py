from pathlib import Path

class Secrets:
    @staticmethod
    def storage_key() -> str:
        key_file = Path("/secrets/storage.key")

        if not key_file.exists():
            raise RuntimeError("Storage key not found in /secrets volume")

        return Path("/secrets/storage.key").read_text().strip()
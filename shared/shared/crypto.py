import os
import logging
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from base64 import b64decode
from pathlib import Path

# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# -----------------------------
# Load AES key
# -----------------------------
def load_aes_key() -> bytes:
    """
    Load AES key from Docker secret or environment variable.
    Supports:
      - Docker secret at /run/secrets/aes_key
      - Environment variable AES_SECRET_KEY (hex or base64)
    Key must be 16, 24, or 32 bytes (AES-128/192/256)
    """
    key_file = Path("/run/secrets/aes_key")
    key_env = os.getenv("AES_SECRET_KEY")
    key: bytes | None = None

    # 1️⃣ Try Docker secret first
    if key_file.exists():
        log.info("Loading AES key from Docker secret")
        key = key_file.read_bytes()
    # 2️⃣ Fall back to environment variable
    elif key_env:
        log.info("Loading AES key from environment variable")
        key_env = key_env.strip()
        try:
            key = bytes.fromhex(key_env)  # hex first
        except ValueError:
            try:
                key = b64decode(key_env)   # fallback to base64
            except Exception as e:
                raise RuntimeError(f"AES_SECRET_KEY is not valid hex or base64: {e}")
    else:
        raise RuntimeError("AES key not found in Docker secret or environment variable")

    # ✅ Validate length
    if len(key) not in (16, 24, 32):
        raise RuntimeError(f"AESGCM key must be 128, 192, or 256 bits. Got {len(key)*8} bits")

    log.info("AES key loaded successfully (%d bytes)", len(key))
    return key

AES_KEY = load_aes_key()

# -----------------------------
# Encryption / Decryption
# -----------------------------
AES_VERSION = 1  # For future key rotation

def encrypt(data: bytes) -> dict:
    """
    Encrypt bytes using AES-GCM.
    Returns JSON-compatible dict with nonce, ciphertext, version.
    """
    log.info("Encrypting data...")
    aesgcm = AESGCM(AES_KEY)
    nonce = os.urandom(12)  # 96-bit unique nonce per encryption
    ciphertext = aesgcm.encrypt(nonce, data, associated_data=None)

    result = {
        "version": AES_VERSION,
        "nonce": nonce.hex(),
        "ciphertext": ciphertext.hex()
    }
    log.info("Encryption complete")
    return result

def decrypt(nonce_hex: str, ciphertext_hex: str) -> bytes:
    """
    Decrypt JSON-compatible AES-GCM encrypted dict.
    """
    log.info("Decrypting data...")
    aesgcm = AESGCM(AES_KEY)
    nonce = bytes.fromhex(nonce_hex)
    ciphertext = bytes.fromhex(ciphertext_hex)
    decrypted = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
    log.info("Decryption complete")
    return decrypted
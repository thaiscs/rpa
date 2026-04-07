import os
import logging
from pathlib import Path
from base64 import b64decode, urlsafe_b64encode
from cryptography import x509
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import (
    pkcs12, Encoding, PrivateFormat, NoEncryption
)
from cryptography.hazmat.primitives.serialization import pkcs12, Encoding, PrivateFormat, NoEncryption

# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# -----------------------------
# Load Fernet key
# -----------------------------
def load_fernet_key() -> bytes:
    key_file = Path("/run/secrets/fernet_key")

    if not key_file.exists():
        raise RuntimeError("Encryption key not found in Docker secret")
    
    # Must be 44 chars of URL-safe base64
    try:
        fernet_key = key_file.read_text().strip().encode()
        Fernet(fernet_key)
        return fernet_key
    except Exception:
        raise RuntimeError("Encryption key is not a valid Fernet key")

FERNET_KEY = load_fernet_key()
fernet = Fernet(FERNET_KEY)

# -----------------------------
# Encryption / Decryption
# -----------------------------
def encrypt(data: bytes) -> dict:
    """
    Encrypt bytes using Fernet.
    Returns dict compatible with JSON.
    """
    log.info("Encrypting data...")
    token = fernet.encrypt(data)
    log.info("Encryption complete")
    return {
        "version": 1,
        "ciphertext": token.decode("utf-8")
    }

def decrypt(ciphertext: str) -> bytes:
    """
    Decrypt data encrypted using Fernet.
    """
    log.info("Decrypting data...")
    try:
        decrypted = fernet.decrypt(ciphertext.encode("utf-8"))
        log.info("Decryption complete")
        return decrypted
    except InvalidToken:
        raise RuntimeError("Invalid encryption token or wrong key.")

# -----------------------------
# Extract cert/key from files
# -----------------------------
def extract_pfx_components(pfx_bytes: bytes, pfx_password: str):
    """
    Extracts:
      - private key (PEM)
      - certificate (PEM)
    """
    try:

        private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
            data=pfx_bytes,
            password=pfx_password.encode()
        )

    except ValueError:
        # This catches "Invalid password or PKCS12 data" and similar issues
        raise

    # Double-check the extracted components
    if private_key is None or certificate is None:
        raise ValueError("Não foi possível extrair a chave ou certificado do arquivo PFX.")
    
    # Convert to PEM format
    private_key_pem = private_key.private_bytes(
        Encoding.PEM,
        PrivateFormat.PKCS8,
        NoEncryption()
    )

    certificate_pem = certificate.public_bytes(Encoding.PEM)

    return private_key_pem, certificate_pem

# -----------------------------
# Extract cert metadata
# -----------------------------
def extract_cert_metadata(cert_pem: bytes):
    cert = x509.load_pem_x509_certificate(cert_pem, default_backend())
    metadata = {
        "cert_issuer": cert.issuer.rfc4514_string(),
        "cert_valid_from": cert.not_valid_before_utc,   # datetime com timezone,
        "cert_valid_to": cert.not_valid_after_utc       # datetime com timezone
    }
    return metadata["cert_issuer"], metadata["cert_valid_from"], metadata["cert_valid_to"]
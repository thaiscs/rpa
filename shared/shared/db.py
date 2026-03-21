import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extras import Json
import os
import time
import logging
from shared.crypto import encrypt
from shared.crypto import decrypt
from shared.crypto import extract_pfx_components
from shared.crypto import extract_cert_metadata

log = logging.getLogger(__name__)

def get_db_connection(retries: int = 10, delay: int = 2):
    """
    Returns a psycopg2 connection.
    Retries 'retries' times with 'delay' seconds if DB is unavailable.
    """
    dbname = os.getenv("POSTGRES_DB", "certsdb")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "postgres")

    last_exception = None
    for attempt in range(1, retries + 1):
        try:
            log.info(f"Attempting DB connection (try {attempt}/{retries})...")
            conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                cursor_factory=RealDictCursor
            )
            log.info("DB connection successful")
            return conn
        except Exception as e:
            last_exception = e
            log.warning(f"DB connection failed (attempt {attempt}): {e}")
            time.sleep(delay)

    log.error("Could not connect to DB after multiple retries")
    raise last_exception


def save_client_cert(legal_name: str, person_type: str, tax_id: str, cert_name: str, cert_bytes: bytes, cert_password: str):
    log.info(f"Saving certificate for CNPJ/CPF={tax_id}, legal_name={legal_name}, cert_name={cert_name}")

    try:
        # Step 1. Upsert do cliente
        print("DEBUG types THAIS:", type(tax_id), type(legal_name), type(person_type))

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO clients (tax_id, legal_name, person_type)
            VALUES (%s, %s, %s)
            ON CONFLICT (tax_id) DO UPDATE SET
                legal_name = EXCLUDED.legal_name,
                person_type = EXCLUDED.person_type
            RETURNING id;
        """, (tax_id, legal_name, person_type))

        row = cur.fetchone()

        if not row:
            raise Exception("INSERT/UPDATE falhou: nenhum id retornado")

        client_id = row["id"]

        # Step 2: extract cert + key
        private_key_pem, certificate_pem = extract_pfx_components(
            cert_bytes,
            cert_password
        )

        # Step 3: encrypt everything
        encrypted_pfx = encrypt(cert_bytes)
        encrypted_password = encrypt(cert_password.encode())
        encrypted_key = encrypt(private_key_pem)
        encrypted_cert = encrypt(certificate_pem)

        # Step 4. Upsert do certificado
        cert_issuer, cert_valid_from, cert_valid_to = extract_cert_metadata(certificate_pem)
        cur.execute("""
            INSERT INTO certificates (
                client_id,
                name,
                encrypted_cert,
                encrypted_key,
                encrypted_pfx,
                encrypted_pfx_password,
                issuer,
                valid_from,
                valid_to
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            client_id,
            cert_name,
            Json(encrypted_cert),
            Json(encrypted_key),
            Json(encrypted_pfx),
            Json(encrypted_password),
            cert_issuer,
            cert_valid_from,
            cert_valid_to
        ))

        conn.commit()
        cur.close()
        conn.close()

        log.info("Client + certificate saved/updated successfully.")

    except Exception as e:
        log.exception("Erro ao salvar certificado")
        raise

# --------------------------------------------------
# Banco → Buscar certificado
# --------------------------------------------------
def fetch_client_cert(client_id: str):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT encrypted_cert, encrypted_key
        FROM certificates
        WHERE client_id = %s
    """, (client_id,))

    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        raise RuntimeError(f"Client {client_id} does not have stored certificates.")

    cert_info = row["encrypted_cert"]
    key_info = row["encrypted_key"]

    cert_bytes = decrypt(cert_info["nonce"], cert_info["ciphertext"])
    key_bytes  = decrypt(key_info["nonce"], key_info["ciphertext"])

    return cert_bytes, key_bytes
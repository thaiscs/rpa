import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extras import Json
import os
import time
import logging
from shared.crypto import encrypt
from shared.crypto import decrypt

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


def save_client_cert(razao_social: str, cnpj_cpf: str, cert_name: str, cert_bytes: bytes):
    log.info(f"Saving certificate for CNPJ/CPF={cnpj_cpf}")

    try:
        encrypted_cert = encrypt(cert_bytes)

        conn = get_db_connection()
        cur = conn.cursor()

        # 1. Upsert do cliente
        cur.execute("""
            INSERT INTO clients (cnpj_cpf, razao_social)
            VALUES (%s, %s)
            ON CONFLICT (cnpj_cpf) DO UPDATE SET
                razao_social = EXCLUDED.razao_social
            RETURNING id;
        """, (cnpj_cpf, razao_social))

        row = cur.fetchone()

        if not row:
            raise Exception("INSERT/UPDATE falhou: nenhum id retornado")

        client_id = row["id"]

        # 2. Upsert do certificado
        cur.execute("""
            INSERT INTO certificates (
                client_id,
                name,
                encrypted_cert,
                encrypted_key,
                encrypted_cert_user,
                encrypted_cert_password
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            client_id,
            cert_name,
            Json(encrypted_cert),
            Json(encrypted_key),
            encrypted_user,
            encrypted_password
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
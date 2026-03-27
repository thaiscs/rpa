from psycopg2.extras import Json
from shared.crypto import encrypt
from shared.crypto import decrypt
from shared.crypto import extract_pfx_components
from shared.crypto import extract_cert_metadata
from shared.conn import db_cursor
import logging

log = logging.getLogger(__name__)

def save_client_cert(legal_name: str, person_type: str, tax_id: str, cert_name: str, cert_bytes: bytes, cert_password: str):
    log.info(f"Saving certificate for CNPJ/CPF={tax_id}, legal_name={legal_name}, cert_name={cert_name}")

    try:
        # Step 1. Upsert do cliente
        with db_cursor() as cur:
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

            log.info("Client + certificate saved/updated successfully.")

    except Exception as e:
        log.exception("Erro ao salvar certificado")
        raise

# --------------------------------------------------
# Banco → Buscar certificado
# --------------------------------------------------
def fetch_client_cert(client_id: str):
    with db_cursor() as cur:

        cur.execute("""
            SELECT encrypted_cert, encrypted_key
            FROM certificates
            WHERE client_id = %s
        """, (client_id,))

        row = cur.fetchone()

        if not row:
            raise RuntimeError(f"Client {client_id} does not have stored certificates.")

        cert_info = row["encrypted_cert"]
        key_info = row["encrypted_key"]

        cert_bytes = decrypt(cert_info["nonce"], cert_info["ciphertext"])
        key_bytes  = decrypt(key_info["nonce"], key_info["ciphertext"])

        return cert_bytes, key_bytes
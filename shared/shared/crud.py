from sqlalchemy import select, insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from shared.models import Client, Certificate
from shared.crypto import encrypt, decrypt, extract_pfx_components, extract_cert_metadata
import logging

log = logging.getLogger(__name__)

async def save_client_cert(
    db: AsyncSession,
    legal_name: str,
    person_type: str,
    tax_id: str,
    cert_name: str,
    cert_bytes: bytes,
    cert_password: str
):
    log.info("Preparing certificate data...")

    try:
        # =========================================================
        # 🧠 STEP 0: CPU / IO HEAVY WORK (OUTSIDE TRANSACTION)
        # =========================================================

        private_key_pem, certificate_pem = extract_pfx_components(
            cert_bytes,
            cert_password
        )

        encrypted_pfx = encrypt(cert_bytes)
        encrypted_password = encrypt(cert_password.encode())
        encrypted_key = encrypt(private_key_pem)
        encrypted_cert = encrypt(certificate_pem)

        cert_issuer, cert_valid_from, cert_valid_to = extract_cert_metadata(
            certificate_pem
        )

        # =========================================================
        # 🔒 STEP 1: DB TRANSACTION (FAST + ATOMIC ONLY)
        # =========================================================

        async with db.begin():

            # Upsert client
            client_stmt = (
                pg_insert(Client)
                .values(
                    tax_id=tax_id,
                    legal_name=legal_name,
                    person_type=person_type
                )
                .on_conflict_do_update(
                    index_elements=["tax_id"],
                    set_={
                        "legal_name": legal_name,
                        "person_type": person_type
                    }
                )
                .returning(Client.id)
            )

            result = await db.execute(client_stmt)
            client_id = result.scalar_one_or_none()

            if not client_id:
                raise RuntimeError("Failed to create or update client")

            # Insert certificate
            cert_stmt = (
                pg_insert(Certificate)
                .values(
                    client_id=client_id,
                    name=cert_name,
                    encrypted_cert=encrypted_cert,
                    encrypted_key=encrypted_key,
                    encrypted_pfx=encrypted_pfx,
                    encrypted_pfx_password=encrypted_password,
                    issuer=cert_issuer,
                    valid_from=cert_valid_from,
                    valid_to=cert_valid_to
                )
                .returning(Certificate.id)
            )

            cert_result = await db.execute(cert_stmt)
            cert_id = cert_result.scalar_one_or_none()

            if not cert_id:
                raise RuntimeError("Failed to create certificate")

        # =========================================================
        # ✅ SUCCESS (OUTSIDE TRANSACTION)
        # =========================================================

        log.info(
            "Client + certificate saved successfully "
            f"(client_id={client_id}, cert_id={cert_id})"
        )

        return {
            "client_id": client_id,
            "cert_id": cert_id
        }

    except Exception:
        log.exception("Failed to save client certificate")
        raise


async def fetch_client_cert(db: AsyncSession, client_id: str):
    stmt = select(Certificate).where(Certificate.client_id == client_id)
    result = await db.execute(stmt)
    cert = result.scalars().first()
    if not cert:
        raise RuntimeError(f"Client {client_id} does not have stored certificates.")

    cert_bytes = decrypt(cert.encrypted_cert["nonce"], cert.encrypted_cert["ciphertext"])
    key_bytes = decrypt(cert.encrypted_key["nonce"], cert.encrypted_key["ciphertext"])

    return cert_bytes, key_bytes
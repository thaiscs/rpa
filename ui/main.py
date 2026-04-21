from nicegui import ui
from pathlib import Path
import pages.login
import pages.dashboard
import pages.add_cert
import pages.clients
import pages.ecac
import pages.login
import pages.signup
import pages.forgot_password
import pages.reset_password

class Secrets:
    @staticmethod
    def storage_key() -> str:
        key_file = Path("/secrets/storage.key")

        if not key_file.exists():
            raise RuntimeError("Storage key not found in /secrets volume")

        return Path("/secrets/storage.key").read_text().strip()
    

ui.run(
    host="0.0.0.0",
    port=3000,
    title="RPA Admin Panel",
    favicon="./assets/icons8-robot-32.png",
    storage_secret=Secrets.storage_key()
)
from pathlib import Path

from nicegui import ui

import pages.add_cert  # noqa: F401  -- side-effect: registers @ui.page
import pages.clients  # noqa: F401
import pages.dashboard  # noqa: F401
import pages.ecac  # noqa: F401
import pages.forgot_password  # noqa: F401
import pages.login  # noqa: F401
import pages.reset_password  # noqa: F401
import pages.signup  # noqa: F401
from helpers.secret import Secrets

ui.add_css(Path(__file__).parent.joinpath("assets/theme.css").read_text(), shared=True)

ui.run(
    host="0.0.0.0",
    port=3000,
    title="RPA Admin Panel",
    favicon="./assets/icons8-robot-32.png",
    storage_secret=Secrets.storage_key(),
)

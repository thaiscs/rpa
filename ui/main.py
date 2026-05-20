from pathlib import Path

from nicegui import ui

import pages.forgot_password  # noqa: F401  -- side-effect: registers @ui.page
import pages.login  # noqa: F401
import pages.reset_password  # noqa: F401
import pages.signup  # noqa: F401
import pages.spa  # noqa: F401  -- catch-all SPA for protected pages; must be last
from components.sidebar import install_nav_assets
from helpers.secret import Secrets

ui.add_css(Path(__file__).parent.joinpath("assets/theme.css").read_text(), shared=True)
install_nav_assets()

ui.run(
    host="0.0.0.0",
    port=3000,
    title="RPA Admin Panel",
    favicon="./assets/icons8-robot-32.png",
    storage_secret=Secrets.storage_key(),
)

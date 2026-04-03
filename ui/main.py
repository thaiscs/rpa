from nicegui import ui
import pages.login
import pages.dashboard
import pages.add_cert
import pages.clients
import pages.ecac

ui.run(host="0.0.0.0", port=3000, title="RPA Admin Panel", favicon="./assets/icons8-robot-32.png")
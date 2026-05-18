from components.cert_form import cert_form
from components.shell import page_shell
from helpers.auth import protected


@protected("/cadastrar-certificado")
def add_cert():
    with page_shell(current="/cadastrar-certificado"):
        cert_form()

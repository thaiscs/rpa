from werkzeug.exceptions import BadRequest

class PFXError(BadRequest):
    def __init__(self, message="Senha do certificado ou arquivo PFX invalidos"):
        super().__init__(description=message)
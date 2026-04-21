def parse_err(message: str | dict | list ) -> str:
    # If message is a dict, try to extract a meaningful string
    if isinstance(message, dict):
        # Common key 'detail', fallback to first value or empty string
        message_text = message.get("detail") or next(iter(message.values()), "")
    elif isinstance(message, list):
        parts = []
        # Assume list of error dicts with 'type', 'msg', and 'loc' keys (like Pydantic/ FastAPI errors)
        for err in message:
            err_type = err.get("type", "")
            err_msg = err.get("msg", "")
            loc = " → ".join(str(x) for x in err.get("loc", []))
            parts.append(f"[{loc}] {err_msg} ({err_type})")
        return "; ".join(parts)    
    else:
        message_text = message

    # Normalize to lowercase for keyword checks
    lower_msg = message_text.lower()

    if "invalid" in lower_msg:
        return "Arquivo ou senha do certificado inválidos."
    elif "missing" in lower_msg:
        return "Todos os campos são obrigatórios."
    elif "cnpj/cpf" in lower_msg:
        return "CNPJ/CPF inválido. Deve conter 11 ou 14 dígitos."
    
    return message_text  # fallback

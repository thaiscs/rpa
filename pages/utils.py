import re

def validate_tax_id(tax_id: str) -> bool:
    """
    Validate tax_id format (CPF or CNPJ)
    """
    digits_only = re.sub(r"\D", "", tax_id)  # remove pontos, traços, barras
    return len(digits_only) in [11, 14]
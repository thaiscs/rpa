import re

def get_person_type(tax_id: str) -> str:
    """
    Define person_type based on tax_id length
    """
    digits_only = re.sub(r"\D", "", tax_id)  # remove pontos, traços, barras
    print("THAIS")     # individual
    if len(digits_only) == 11:
      return "individual"
    elif len(digits_only) == 14:
      return "company"
    else:
      return "other"
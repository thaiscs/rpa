
from shared.utils import get_person_type


class TestGetPersonType:
    """Tests for get_person_type function."""

    def test_returns_individual_for_cpf(self):
        """Test that CPF (11 digits) returns 'individual'."""
        assert get_person_type("123.456.789-01") == "individual"
        assert get_person_type("12345678901") == "individual"

    def test_returns_company_for_cnpj(self):
        """Test that CNPJ (14 digits) returns 'company'."""
        assert get_person_type("12.345.678/0001-90") == "company"
        assert get_person_type("12345678000190") == "company"

    def test_returns_other_for_invalid_length(self):
        """Test that invalid lengths return 'other'."""
        assert get_person_type("123") == "other"
        assert get_person_type("123456789012345") == "other"
        assert get_person_type("") == "other"

    def test_handles_mixed_formats(self):
        """Test that formatting characters are handled correctly."""
        # CPF with dots and dash
        assert get_person_type("123.456.789-01") == "individual"
        # CNPJ with dots, slash, and dash
        assert get_person_type("12.345.678/0001-90") == "company"
        # With slashes
        assert get_person_type("123/456/789-01") == "individual"

    def test_handles_non_numeric_characters(self):
        """Test that non-numeric characters are stripped."""
        assert get_person_type("abc123.456.789-01xyz") == "individual"
        assert get_person_type("12.345.678/0001-90!@#") == "company"


from ui.helpers.validation import validate_tax_id


class TestValidateTaxId:
    """Tests for validate_tax_id function."""

    def test_valid_cpf(self):
        """Test validation of valid CPF."""
        assert validate_tax_id("123.456.789-01") is True
        assert validate_tax_id("12345678901") is True

    def test_valid_cnpj(self):
        """Test validation of valid CNPJ."""
        assert validate_tax_id("12.345.678/0001-90") is True
        assert validate_tax_id("12345678000190") is True

    def test_invalid_length(self):
        """Test validation of invalid lengths."""
        assert validate_tax_id("123") is False
        assert validate_tax_id("123456789012345") is False
        assert validate_tax_id("") is False

    def test_with_formatting(self):
        """Test validation with formatting characters."""
        assert validate_tax_id("123.456.789-01") is True
        assert validate_tax_id("12.345.678/0001-90") is True

    def test_with_non_numeric(self):
        """Test validation with non-numeric characters."""
        assert validate_tax_id("abc123.456.789-01xyz") is True  # 11 digits
        assert validate_tax_id("12.345.678/0001-90!@#") is True  # 14 digits

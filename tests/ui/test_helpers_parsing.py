
from ui.helpers.parsing import parse_err


class TestParseErr:
    """Tests for parse_err function."""

    def test_parse_string_message(self):
        """Test parsing a simple string message."""
        result = parse_err("Simple error message")
        assert result == "Simple error message"

    def test_parse_dict_with_detail(self):
        """Test parsing dict with 'detail' key."""
        message = {"detail": "Detailed error message"}
        result = parse_err(message)
        assert result == "Detailed error message"

    def test_parse_dict_without_detail(self):
        """Test parsing dict without 'detail' key."""
        message = {"error": "Some error"}
        result = parse_err(message)
        assert result == "Some error"

    def test_parse_dict_empty(self):
        """Test parsing empty dict."""
        message = {}
        result = parse_err(message)
        assert result == ""

    def test_parse_list_of_errors(self):
        """Test parsing list of error dicts."""
        message = [
            {"type": "value_error", "msg": "Field required", "loc": ["body", "field1"]},
            {"type": "value_error", "msg": "Invalid email", "loc": ["body", "email"]}
        ]
        result = parse_err(message)
        assert "field1" in result.lower()
        assert "email" in result.lower()

    def test_parse_list_with_missing_keys(self):
        """Test parsing list with missing keys."""
        message = [{"msg": "Error message"}]
        result = parse_err(message)
        assert "Error message" in result

    def test_normalize_invalid_keyword(self):
        """Test normalization of 'invalid' keyword."""
        result = parse_err("Invalid certificate")
        assert result == "Arquivo ou senha do certificado inválidos."

    def test_normalize_missing_keyword(self):
        """Test normalization of 'missing' keyword."""
        result = parse_err("Field is missing")
        assert result == "Todos os campos são obrigatórios."

    def test_normalize_cnpj_cpf_keyword(self):
        """Test normalization of 'cnpj/cpf' keyword."""
        result = parse_err("Invalid CNPJ/CPF format")
        assert result == "CNPJ/CPF inválido. Deve conter 11 ou 14 dígitos."

    def test_normalize_case_insensitive(self):
        """Test that keyword matching is case insensitive."""
        result = parse_err("INVALID certificate")
        assert result == "Arquivo ou senha do certificado inválidos."

    def test_fallback_to_original(self):
        """Test fallback to original message when no keyword matches."""
        result = parse_err("Some other error")
        assert result == "Some other error"

    def test_parse_dict_with_invalid_keyword(self):
        """Test parsing dict with 'invalid' in detail."""
        message = {"detail": "Invalid password"}
        result = parse_err(message)
        assert result == "Arquivo ou senha do certificado inválidos."

    def test_parse_list_with_invalid_keyword(self):
        """Test parsing list with 'invalid' in error message."""
        message = [{"type": "value_error", "msg": "Invalid value", "loc": ["body"]}]
        result = parse_err(message)
        # List parsing takes precedence over keyword normalization
        assert "invalid value" in result.lower()

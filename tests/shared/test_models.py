
from shared.models.certificate import Certificate
from shared.models.client import Client, PersonTypeEnum
from shared.models.user import User


class TestUser:
    """Tests for User model."""

    def test_user_table_name(self):
        """Test that User has correct table name."""
        assert User.__tablename__ == "users"

    def test_user_has_required_fields(self):
        """Test that User has required fields from FastAPI Users."""
        # FastAPI Users provides: id, email, hashed_password, is_active, is_superuser, is_verified
        # Our custom fields: name, client_id
        assert hasattr(User, 'id')
        assert hasattr(User, 'email')
        assert hasattr(User, 'hashed_password')
        assert hasattr(User, 'is_active')
        assert hasattr(User, 'is_superuser')
        assert hasattr(User, 'is_verified')
        assert hasattr(User, 'name')
        assert hasattr(User, 'client_id')


class TestClient:
    """Tests for Client model."""

    def test_client_table_name(self):
        """Test that Client has correct table name."""
        assert Client.__tablename__ == "clients"

    def test_client_has_required_fields(self):
        """Test that Client has required fields."""
        assert hasattr(Client, 'id')
        assert hasattr(Client, 'legal_name')
        assert hasattr(Client, 'tax_id')
        assert hasattr(Client, 'person_type')
        assert hasattr(Client, 'created_at')
        assert hasattr(Client, 'updated_at')

    def test_client_person_type_enum(self):
        """Test that PersonTypeEnum has correct values."""
        assert PersonTypeEnum.individual.value == "individual"
        assert PersonTypeEnum.company.value == "company"
        assert PersonTypeEnum.mei.value == "mei"
        assert PersonTypeEnum.other.value == "other"


class TestCertificate:
    """Tests for Certificate model."""

    def test_certificate_table_name(self):
        """Test that Certificate has correct table name."""
        assert Certificate.__tablename__ == "certificates"

    def test_certificate_has_required_fields(self):
        """Test that Certificate has required fields."""
        assert hasattr(Certificate, 'id')
        assert hasattr(Certificate, 'client_id')
        assert hasattr(Certificate, 'name')
        assert hasattr(Certificate, 'encrypted_pfx')
        assert hasattr(Certificate, 'encrypted_pfx_password')
        assert hasattr(Certificate, 'encrypted_cert')
        assert hasattr(Certificate, 'encrypted_key')
        assert hasattr(Certificate, 'issuer')
        assert hasattr(Certificate, 'valid_from')
        assert hasattr(Certificate, 'valid_to')
        assert hasattr(Certificate, 'expired')
        assert hasattr(Certificate, 'created_at')
        assert hasattr(Certificate, 'updated_at')

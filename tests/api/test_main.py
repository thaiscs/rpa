
from api.main import app


class TestMainApp:
    """Tests for main FastAPI app configuration."""

    def test_app_is_created(self):
        """Test that FastAPI app is created."""
        assert app is not None
        assert app.title == "RPA Backend"
        assert app.version == "1.0.0"

    def test_app_has_routes(self):
        """Test that app has routes registered."""
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        assert len(routes) > 0

    def test_auth_routes_registered(self):
        """Test that auth routes are registered."""
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        assert any("/auth" in route for route in routes)

    def test_users_routes_registered(self):
        """Test that users routes are registered."""
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        assert any("/users" in route for route in routes)

    def test_admin_routes_registered(self):
        """Test that admin routes are registered."""
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        assert any("/admin" in route for route in routes)

"""
API tests for authentication endpoints.

Covers:
- User registration
- Duplicate email/username handling
- Login
- Invalid credentials
- Current-user authentication
- Logout
"""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_current_user, get_db
from app.main import app
from app.models.user import User


AUTH_PREFIX = "/api/auth"


@pytest.fixture
def client():
    """Create a FastAPI test client."""

    return TestClient(app)


@pytest.fixture
def db():
    """Provide a mocked database session."""

    return MagicMock()


@pytest.fixture
def sample_user():
    """Create a complete sample user for API tests."""

    now = datetime.now(UTC)

    return User(
        id=uuid4(),
        full_name="Test User",
        username="testuser",
        email="test@example.com",
        password_hash="hashed-password",
        role="user",
        is_active=True,
        is_verified=True,
        is_superuser=False,
        created_at=now,
        updated_at=now,
    )


class TestRegister:
    """Tests for POST /api/auth/register."""

    @patch("app.api.v1.auth.UserService")
    def test_register_success(
        self,
        mock_service_class,
        client,
        db,
        sample_user,
    ):
        mock_service = mock_service_class.return_value

        mock_service.get_by_email.return_value = None
        mock_service.get_by_username.return_value = None
        mock_service.create_user.return_value = sample_user

        app.dependency_overrides[get_db] = lambda: db

        try:
            response = client.post(
                f"{AUTH_PREFIX}/register",
                json={
                    "full_name": "Test User",
                    "username": "testuser",
                    "email": "test@example.com",
                    "password": "StrongPassword123",
                },
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 201

        data = response.json()

        assert data["id"] == str(sample_user.id)
        assert data["full_name"] == "Test User"
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

        mock_service.create_user.assert_called_once()

    @patch("app.api.v1.auth.UserService")
    def test_register_duplicate_email(
        self,
        mock_service_class,
        client,
        db,
        sample_user,
    ):
        mock_service = mock_service_class.return_value

        mock_service.get_by_email.return_value = sample_user

        app.dependency_overrides[get_db] = lambda: db

        try:
            response = client.post(
                f"{AUTH_PREFIX}/register",
                json={
                    "full_name": "Another User",
                    "username": "anotheruser",
                    "email": "test@example.com",
                    "password": "StrongPassword123",
                },
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 409
        assert response.json()["detail"] == "Email already exists."

        mock_service.create_user.assert_not_called()

    @patch("app.api.v1.auth.UserService")
    def test_register_duplicate_username(
        self,
        mock_service_class,
        client,
        db,
        sample_user,
    ):
        mock_service = mock_service_class.return_value

        mock_service.get_by_email.return_value = None
        mock_service.get_by_username.return_value = sample_user

        app.dependency_overrides[get_db] = lambda: db

        try:
            response = client.post(
                f"{AUTH_PREFIX}/register",
                json={
                    "full_name": "Another User",
                    "username": "testuser",
                    "email": "another@example.com",
                    "password": "StrongPassword123",
                },
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 409
        assert response.json()["detail"] == "Username already exists."

        mock_service.create_user.assert_not_called()

    @patch("app.api.v1.auth.UserService")
    def test_register_integrity_error(
        self,
        mock_service_class,
        client,
        db,
    ):
        mock_service = mock_service_class.return_value

        mock_service.get_by_email.return_value = None
        mock_service.get_by_username.return_value = None

        mock_service.create_user.side_effect = IntegrityError(
            "INSERT",
            {},
            Exception("duplicate key"),
        )

        app.dependency_overrides[get_db] = lambda: db

        try:
            response = client.post(
                f"{AUTH_PREFIX}/register",
                json={
                    "full_name": "Test User",
                    "username": "testuser",
                    "email": "test@example.com",
                    "password": "StrongPassword123",
                },
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 409
        assert (
            response.json()["detail"]
            == "Email or username already exists."
        )

        db.rollback.assert_called_once()


class TestLogin:
    """Tests for POST /api/auth/login."""

    @patch("app.api.v1.auth.create_access_token")
    @patch("app.api.v1.auth.UserService")
    def test_login_success(
        self,
        mock_service_class,
        mock_create_token,
        client,
        db,
        sample_user,
    ):
        mock_service = mock_service_class.return_value
        mock_service.authenticate.return_value = sample_user
        mock_create_token.return_value = "test-access-token"

        app.dependency_overrides[get_db] = lambda: db

        try:
            response = client.post(
                f"{AUTH_PREFIX}/login",
                json={
                    "email": "test@example.com",
                    "password": "StrongPassword123",
                },
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200

        data = response.json()

        assert data["access_token"] == "test-access-token"
        assert data["token_type"] == "bearer"

        mock_service.authenticate.assert_called_once_with(
            "test@example.com",
            "StrongPassword123",
        )

        mock_create_token.assert_called_once()

    @patch("app.api.v1.auth.UserService")
    def test_login_invalid_credentials(
        self,
        mock_service_class,
        client,
        db,
    ):
        mock_service = mock_service_class.return_value
        mock_service.authenticate.return_value = None

        app.dependency_overrides[get_db] = lambda: db

        try:
            response = client.post(
                f"{AUTH_PREFIX}/login",
                json={
                    "email": "unknown@example.com",
                    "password": "WrongPassword",
                },
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 401

        data = response.json()

        assert data["detail"] == "Invalid email or password."
        assert response.headers["www-authenticate"] == "Bearer"

    def test_login_invalid_payload(
        self,
        client,
        db,
    ):
        app.dependency_overrides[get_db] = lambda: db

        try:
            response = client.post(
                f"{AUTH_PREFIX}/login",
                json={
                    "email": "not-an-email",
                    "password": "",
                },
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 422


class TestCurrentUser:
    """Tests for GET /api/auth/me."""

    def test_me_success(
        self,
        client,
    ):
        current_user = {
            "sub": str(uuid4()),
            "type": "access",
            "role": "user",
            "email": "test@example.com",
        }

        app.dependency_overrides[get_current_user] = (
            lambda: current_user
        )

        try:
            response = client.get(
                f"{AUTH_PREFIX}/me"
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        assert response.json() == current_user

    def test_me_without_token(
        self,
        client,
    ):
        response = client.get(
            f"{AUTH_PREFIX}/me"
        )

        assert response.status_code == 401


class TestLogout:
    """Tests for POST /api/auth/logout."""

    def test_logout(self, client):
        response = client.post(
            f"{AUTH_PREFIX}/logout"
        )

        assert response.status_code == 200

        assert response.json() == {
            "message": (
                "Logout acknowledged. "
                "Remove the access token on the client."
            ),
        }
"""
Unit tests for UserService.
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import UserService


class TestUserServiceCreate:
    """Tests for user creation."""

    @patch("app.services.user_service.hash_password")
    def test_create_user_hashes_password(
        self,
        mock_hash_password,
    ):
        db = MagicMock()
        mock_hash_password.return_value = "hashed-password"

        service = UserService(db)

        data = UserCreate(
            full_name="Test User",
            username="testuser",
            email="TEST@EXAMPLE.COM",
            password="StrongPassword123",
        )

        user = service.create_user(data)

        assert user.full_name == "Test User"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed-password"

        mock_hash_password.assert_called_once_with(
            "StrongPassword123"
        )

        db.add.assert_called_once_with(user)
        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(user)


class TestUserServiceRead:
    """Tests for reading users."""

    def test_get_user(self):
        db = MagicMock()

        expected_user = User(
            id=uuid4(),
            full_name="Test User",
            username="testuser",
            email="test@example.com",
            password_hash="hashed-password",
        )

        db.get.return_value = expected_user

        service = UserService(db)

        result = service.get_user(expected_user.id)

        assert result is expected_user

        db.get.assert_called_once_with(
            User,
            expected_user.id,
        )

    def test_get_by_email_normalizes_email(self):
        db = MagicMock()

        expected_user = User(
            id=uuid4(),
            full_name="Test User",
            username="testuser",
            email="test@example.com",
            password_hash="hashed-password",
        )

        db.scalar.return_value = expected_user

        service = UserService(db)

        result = service.get_by_email(
            "  TEST@EXAMPLE.COM  "
        )

        assert result is expected_user
        db.scalar.assert_called_once()

    def test_get_by_email_rejects_non_string(self):
        db = MagicMock()

        service = UserService(db)

        with pytest.raises(TypeError):
            service.get_by_email(None)  # type: ignore[arg-type]

    def test_get_by_email_empty_returns_none(self):
        db = MagicMock()

        service = UserService(db)

        result = service.get_by_email("   ")

        assert result is None
        db.scalar.assert_not_called()

    def test_get_by_username_normalizes_username(self):
        db = MagicMock()

        expected_user = User(
            id=uuid4(),
            full_name="Test User",
            username="testuser",
            email="test@example.com",
            password_hash="hashed-password",
        )

        db.scalar.return_value = expected_user

        service = UserService(db)

        result = service.get_by_username(
            "  testuser  "
        )

        assert result is expected_user
        db.scalar.assert_called_once()

    def test_get_by_username_empty_returns_none(self):
        db = MagicMock()

        service = UserService(db)

        result = service.get_by_username("   ")

        assert result is None
        db.scalar.assert_not_called()


class TestUserServiceUpdate:
    """Tests for updating users."""

    @patch("app.services.user_service.hash_password")
    def test_update_user_hashes_new_password(
        self,
        mock_hash_password,
    ):
        db = MagicMock()
        mock_hash_password.return_value = "new-hash"

        user = User(
            id=uuid4(),
            full_name="Old Name",
            username="olduser",
            email="old@example.com",
            password_hash="old-hash",
        )

        service = UserService(db)

        data = UserUpdate(
            full_name="New Name",
            password="NewPassword123",
        )

        result = service.update_user(user, data)

        assert result is user
        assert user.full_name == "New Name"
        assert user.password_hash == "new-hash"

        mock_hash_password.assert_called_once_with(
            "NewPassword123"
        )

        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(user)

    def test_update_user_normalizes_email_and_username(self):
        db = MagicMock()

        user = User(
            id=uuid4(),
            full_name="Test User",
            username="olduser",
            email="old@example.com",
            password_hash="hashed-password",
        )

        service = UserService(db)

        data = UserUpdate(
            email="  NEW@EXAMPLE.COM  ",
            username="  newuser  ",
        )

        result = service.update_user(user, data)

        assert result.email == "new@example.com"
        assert result.username == "newuser"

        db.commit.assert_called_once()

    def test_update_user_with_no_changes(self):
        db = MagicMock()

        user = User(
            id=uuid4(),
            full_name="Test User",
            username="testuser",
            email="test@example.com",
            password_hash="hashed-password",
        )

        service = UserService(db)

        data = UserUpdate()

        result = service.update_user(user, data)

        assert result is user
        db.commit.assert_not_called()
        db.refresh.assert_not_called()

    def test_update_user_rejects_empty_email(self):
        with pytest.raises(ValueError):
            UserUpdate(email="   ")

    def test_update_user_rejects_empty_username(self):
        db = MagicMock()

        user = User(
            id=uuid4(),
            full_name="Test User",
            username="testuser",
            email="test@example.com",
            password_hash="hashed-password",
        )

        service = UserService(db)

        data = UserUpdate(username="   ")

        with pytest.raises(
            ValueError,
            match="username cannot be empty",
        ):
            service.update_user(user, data)

        db.commit.assert_not_called()


class TestUserServiceDelete:
    """Tests for deleting users."""

    def test_delete_user(self):
        db = MagicMock()

        user = User(
            id=uuid4(),
            full_name="Test User",
            username="testuser",
            email="test@example.com",
            password_hash="hashed-password",
        )

        service = UserService(db)

        result = service.delete_user(user)

        assert result is None

        db.delete.assert_called_once_with(user)
        db.commit.assert_called_once()


class TestUserServiceAuthentication:
    """Tests for authentication."""

    @patch("app.services.user_service.verify_password")
    def test_authenticate_success(
        self,
        mock_verify_password,
    ):
        db = MagicMock()

        user = User(
            id=uuid4(),
            full_name="Test User",
            username="testuser",
            email="test@example.com",
            password_hash="hashed-password",
        )

        mock_verify_password.return_value = True
        db.scalar.return_value = user

        service = UserService(db)

        result = service.authenticate(
            " TEST@EXAMPLE.COM ",
            "StrongPassword123",
        )

        assert result is user

        mock_verify_password.assert_called_once_with(
            "StrongPassword123",
            "hashed-password",
        )

    def test_authenticate_unknown_user(self):
        db = MagicMock()
        db.scalar.return_value = None

        service = UserService(db)

        result = service.authenticate(
            "unknown@example.com",
            "StrongPassword123",
        )

        assert result is None

    @patch("app.services.user_service.verify_password")
    def test_authenticate_wrong_password(
        self,
        mock_verify_password,
    ):
        db = MagicMock()

        user = User(
            id=uuid4(),
            full_name="Test User",
            username="testuser",
            email="test@example.com",
            password_hash="hashed-password",
        )

        db.scalar.return_value = user
        mock_verify_password.return_value = False

        service = UserService(db)

        result = service.authenticate(
            "test@example.com",
            "WrongPassword",
        )

        assert result is None

    def test_authenticate_invalid_email_type(self):
        db = MagicMock()

        service = UserService(db)

        result = service.authenticate(
            None,  # type: ignore[arg-type]
            "password",
        )

        assert result is None

    def test_authenticate_invalid_password_type(self):
        db = MagicMock()

        service = UserService(db)

        result = service.authenticate(
            "test@example.com",
            None,  # type: ignore[arg-type]
        )

        assert result is None

    def test_authenticate_empty_credentials(self):
        db = MagicMock()

        service = UserService(db)

        assert service.authenticate(
            "",
            "password",
        ) is None

        assert service.authenticate(
            "test@example.com",
            "",
        ) is None


class TestUserServicePagination:
    """Tests for user listing."""

    def test_list_users_rejects_negative_skip(self):
        db = MagicMock()

        service = UserService(db)

        with pytest.raises(
            ValueError,
            match="skip must be greater than or equal to 0",
        ):
            service.list_users(skip=-1)

    def test_list_users_rejects_invalid_limit(self):
        db = MagicMock()

        service = UserService(db)

        with pytest.raises(
            ValueError,
            match="limit must be between 1 and 100",
        ):
            service.list_users(limit=101)

    def test_list_users_returns_users(self):
        db = MagicMock()

        users = [
            User(
                id=uuid4(),
                full_name="User One",
                username="userone",
                email="one@example.com",
                password_hash="hash",
            ),
            User(
                id=uuid4(),
                full_name="User Two",
                username="usertwo",
                email="two@example.com",
                password_hash="hash",
            ),
        ]

        db.scalars.return_value.all.return_value = users

        service = UserService(db)

        result = service.list_users(
            skip=0,
            limit=20,
        )

        assert result == users
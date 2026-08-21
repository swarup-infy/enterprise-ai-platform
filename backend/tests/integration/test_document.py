"""
Integration tests for the Document model.

Verifies that:
- Documents can be persisted.
- Documents belong to the correct owner.
- Documents can be retrieved.
- Document metadata is persisted correctly.
- Documents are deleted correctly.
- The owner relationship works correctly.
- The same checksum is allowed for different owners.
- The same checksum is rejected for the same owner.
"""

from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import engine
from app.models.document import Document
from app.models.user import User


@pytest.fixture
def db():
    """Provide a database session for integration tests."""

    with Session(engine) as session:
        yield session
        session.rollback()


@pytest.fixture
def test_user(db: Session):
    """Create a temporary user for document tests."""

    user = User(
        id=uuid4(),
        full_name="Document Test User",
        username=f"document_user_{uuid4().hex[:8]}",
        email=f"{uuid4().hex[:8]}@example.com",
        password_hash="test-password-hash",
        role="user",
        is_active=True,
        is_verified=False,
        is_superuser=False,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    yield user

    db.delete(user)
    db.commit()


class TestDocumentDatabaseIntegration:
    """Integration tests for Document persistence."""

    def test_create_and_read_document(
        self,
        db: Session,
        test_user: User,
    ):
        """Verify a document can be created and retrieved."""

        document = Document(
            id=uuid4(),
            owner_id=test_user.id,
            filename="test-document.pdf",
            original_filename="original-document.pdf",
            file_path="uploads/test-document.pdf",
            mime_type="application/pdf",
            file_size=1024,
            checksum=uuid4().hex,
            title="Test Document",
            summary="Integration test document.",
            embedding_model="BAAI/bge-small-en-v1.5",
            vector_collection="documents",
            is_processed=True,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        assert document.id is not None
        assert document.owner_id == test_user.id
        assert document.filename == "test-document.pdf"
        assert document.original_filename == "original-document.pdf"
        assert document.mime_type == "application/pdf"
        assert document.file_size == 1024
        assert document.title == "Test Document"
        assert document.summary == "Integration test document."
        assert document.is_processed is True

        saved_document = db.scalar(
            select(Document).where(
                Document.id == document.id
            )
        )

        assert saved_document is not None
        assert saved_document.id == document.id
        assert saved_document.owner_id == test_user.id

        db.delete(saved_document)
        db.commit()

    def test_document_owner_relationship(
        self,
        db: Session,
        test_user: User,
    ):
        """Verify a document resolves its owner correctly."""

        document = Document(
            id=uuid4(),
            owner_id=test_user.id,
            filename="owner-test.pdf",
            original_filename="owner-test.pdf",
            file_path="uploads/owner-test.pdf",
            mime_type="application/pdf",
            file_size=2048,
            checksum=uuid4().hex,
            is_processed=False,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        assert document.owner is not None
        assert document.owner.id == test_user.id
        assert document.owner.username == test_user.username

        db.delete(document)
        db.commit()

    def test_document_default_processing_state(
        self,
        db: Session,
        test_user: User,
    ):
        """Verify new documents default to unprocessed."""

        document = Document(
            id=uuid4(),
            owner_id=test_user.id,
            filename="default-test.pdf",
            original_filename="default-test.pdf",
            file_path="uploads/default-test.pdf",
            mime_type="application/pdf",
            file_size=512,
            checksum=uuid4().hex,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        assert document.is_processed is False

        db.delete(document)
        db.commit()

    def test_document_delete(
        self,
        db: Session,
        test_user: User,
    ):
        """Verify a document can be deleted."""

        document = Document(
            id=uuid4(),
            owner_id=test_user.id,
            filename="delete-test.pdf",
            original_filename="delete-test.pdf",
            file_path="uploads/delete-test.pdf",
            mime_type="application/pdf",
            file_size=256,
            checksum=uuid4().hex,
        )

        document_id = document.id

        db.add(document)
        db.commit()

        db.delete(document)
        db.commit()

        deleted_document = db.scalar(
            select(Document).where(
                Document.id == document_id
            )
        )

        assert deleted_document is None

    def test_same_checksum_allowed_for_different_owners(
        self,
        db: Session,
        test_user: User,
    ):
        """Verify the same checksum is allowed for different owners."""

        second_user = User(
            id=uuid4(),
            full_name="Second Document User",
            username=f"second_user_{uuid4().hex[:8]}",
            email=f"{uuid4().hex[:8]}@example.com",
            password_hash="test-password-hash",
            role="user",
            is_active=True,
            is_verified=False,
            is_superuser=False,
        )

        db.add(second_user)
        db.commit()
        db.refresh(second_user)

        checksum = uuid4().hex

        document_one = Document(
            id=uuid4(),
            owner_id=test_user.id,
            filename="user-one.pdf",
            original_filename="user-one.pdf",
            file_path="uploads/user-one.pdf",
            mime_type="application/pdf",
            file_size=100,
            checksum=checksum,
        )

        document_two = Document(
            id=uuid4(),
            owner_id=second_user.id,
            filename="user-two.pdf",
            original_filename="user-two.pdf",
            file_path="uploads/user-two.pdf",
            mime_type="application/pdf",
            file_size=100,
            checksum=checksum,
        )

        db.add_all([document_one, document_two])
        db.commit()

        assert document_one.checksum == document_two.checksum
        assert document_one.owner_id != document_two.owner_id

        db.delete(document_one)
        db.delete(document_two)
        db.delete(second_user)
        db.commit()

    def test_same_checksum_rejected_for_same_owner(
        self,
        db: Session,
        test_user: User,
    ):
        """Verify the same checksum is rejected for the same owner."""

        checksum = uuid4().hex

        document_one = Document(
            id=uuid4(),
            owner_id=test_user.id,
            filename="duplicate-one.pdf",
            original_filename="duplicate-one.pdf",
            file_path="uploads/duplicate-one.pdf",
            mime_type="application/pdf",
            file_size=100,
            checksum=checksum,
        )

        db.add(document_one)
        db.commit()

        document_two = Document(
            id=uuid4(),
            owner_id=test_user.id,
            filename="duplicate-two.pdf",
            original_filename="duplicate-two.pdf",
            file_path="uploads/duplicate-two.pdf",
            mime_type="application/pdf",
            file_size=100,
            checksum=checksum,
        )

        db.add(document_two)

        with pytest.raises(IntegrityError):
            db.commit()

        db.rollback()

        db.delete(document_one)
        db.commit()
"""Tests for session storage functionality."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest
from claude_code_sdk.types import UserMessage

from claude_code_session_client._internal.session_storage import (
    SessionData,
    SimpleSessionPersistence,
)


class TestSessionData:
    """Test SessionData functionality."""

    def test_session_data_creation(self):
        """Test creating SessionData."""
        session_data = SessionData(
            session_id="test-session",
            start_time=datetime.now(),
            last_activity=datetime.now(),
            working_directory="/tmp",
        )

        assert session_data.session_id == "test-session"
        assert session_data.working_directory == "/tmp"
        assert len(session_data.conversation_history) == 0

    def test_add_message(self):
        """Test adding messages to session data."""
        session_data = SessionData(
            session_id="test-session",
            start_time=datetime.now(),
            last_activity=datetime.now(),
        )

        message = UserMessage(content="Hello")
        session_data.add_message(message)

        assert len(session_data.conversation_history) == 1
        assert session_data.conversation_history[0] == message

    def test_serialization(self):
        """Test serialization and deserialization."""
        original = SessionData(
            session_id="test-session",
            start_time=datetime(2023, 1, 1, 12, 0, 0),
            last_activity=datetime(2023, 1, 1, 12, 5, 0),
            working_directory="/tmp",
        )

        # Add a message
        original.add_message(UserMessage(content="Hello"))

        # Serialize to dict
        data_dict = original.to_dict()

        # Deserialize back
        restored = SessionData.from_dict(data_dict)

        assert restored.session_id == original.session_id
        assert restored.start_time == original.start_time
        assert restored.last_activity.replace(microsecond=0) == original.last_activity.replace(
            microsecond=0
        )
        assert restored.working_directory == original.working_directory
        assert len(restored.conversation_history) == 1


class TestSimpleSessionPersistence:
    """Test SimpleSessionPersistence functionality."""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def persistence(self, temp_storage):
        """Create SimpleSessionPersistence instance."""
        return SimpleSessionPersistence(temp_storage)

    def test_init_creates_directory(self, temp_storage):
        """Test that initialization creates storage directory."""
        storage_path = temp_storage / "sessions"
        SimpleSessionPersistence(storage_path)

        assert storage_path.exists()
        assert storage_path.is_dir()

    @pytest.mark.trio
    async def test_save_and_load_session(self, persistence):
        """Test saving and loading session data."""
        session_data = SessionData(
            session_id="test-session",
            start_time=datetime(2023, 1, 1, 12, 0, 0),
            last_activity=datetime(2023, 1, 1, 12, 5, 0),
            working_directory="/tmp",
        )
        session_data.add_message(UserMessage(content="Hello"))

        # Save session
        await persistence.save_session(session_data)

        # Load session
        loaded = await persistence.load_session("test-session")

        assert loaded is not None
        assert loaded.session_id == session_data.session_id
        assert loaded.working_directory == session_data.working_directory
        assert len(loaded.conversation_history) == 1

    @pytest.mark.trio
    async def test_load_nonexistent_session(self, persistence):
        """Test loading a session that doesn't exist."""
        loaded = await persistence.load_session("nonexistent")
        assert loaded is None

    @pytest.mark.trio
    async def test_list_sessions(self, persistence):
        """Test listing sessions."""
        # Initially empty
        sessions = await persistence.list_sessions()
        assert sessions == []

        # Save a session
        session_data = SessionData(
            session_id="test-session",
            start_time=datetime.now(),
            last_activity=datetime.now(),
        )
        await persistence.save_session(session_data)

        # Check list
        sessions = await persistence.list_sessions()
        assert sessions == ["test-session"]

    @pytest.mark.trio
    async def test_delete_session(self, persistence):
        """Test deleting a session."""
        # Save a session
        session_data = SessionData(
            session_id="test-session",
            start_time=datetime.now(),
            last_activity=datetime.now(),
        )
        await persistence.save_session(session_data)

        # Verify it exists
        sessions = await persistence.list_sessions()
        assert "test-session" in sessions

        # Delete it
        deleted = await persistence.delete_session("test-session")
        assert deleted is True

        # Verify it's gone
        sessions = await persistence.list_sessions()
        assert "test-session" not in sessions

        # Try deleting again
        deleted = await persistence.delete_session("test-session")
        assert deleted is False

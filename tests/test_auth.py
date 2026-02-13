"""Tests for gmail_organizer.auth module."""

import json
import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch

from cryptography.fernet import Fernet

from gmail_organizer.auth import GmailAuthenticator, _get_or_create_key


class TestKeyManagement:
    def test_create_new_key(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".key") as f:
            path = f.name
        os.unlink(path)
        key = _get_or_create_key(path)
        assert isinstance(key, bytes)
        Fernet(key)  # Validates it's a proper key
        os.unlink(path)

    def test_read_existing_key(self):
        key = Fernet.generate_key()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".key") as f:
            f.write(key)
            path = f.name
        result = _get_or_create_key(path)
        assert result == key
        os.unlink(path)


class TestGmailAuthenticator:
    def test_init(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            auth = GmailAuthenticator(
                credentials_file=os.path.join(tmpdir, "creds.json"),
                token_file=os.path.join(tmpdir, "token.pickle"),
                key_file=os.path.join(tmpdir, "test.key"),
            )
            assert auth.credentials_file.endswith("creds.json")

    def test_load_token_no_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            auth = GmailAuthenticator(
                token_file=os.path.join(tmpdir, "nonexistent.pickle"),
                key_file=os.path.join(tmpdir, "test.key"),
            )
            assert auth._load_token() is None

    def test_load_token_corrupted(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            token_path = os.path.join(tmpdir, "token.pickle")
            with open(token_path, "wb") as f:
                f.write(b"corrupted")
            auth = GmailAuthenticator(
                token_file=token_path,
                key_file=os.path.join(tmpdir, "test.key"),
            )
            assert auth._load_token() is None

    def test_save_token_encrypted(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            auth = GmailAuthenticator(
                token_file=os.path.join(tmpdir, "token.pickle"),
                key_file=os.path.join(tmpdir, "test.key"),
            )
            mock_creds = MagicMock()
            mock_creds.token = "access"
            mock_creds.refresh_token = "refresh"
            mock_creds.token_uri = "https://oauth2.googleapis.com/token"
            mock_creds.client_id = "cid"
            mock_creds.client_secret = "csecret"
            mock_creds.scopes = ["https://mail.google.com/"]

            auth._save_token(mock_creds)
            assert os.path.exists(os.path.join(tmpdir, "token.pickle"))

    def test_run_auth_flow_no_credentials(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            auth = GmailAuthenticator(
                credentials_file=os.path.join(tmpdir, "nonexistent.json"),
                key_file=os.path.join(tmpdir, "test.key"),
            )
            with pytest.raises(SystemExit):
                auth._run_auth_flow()

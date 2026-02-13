"""
Authentication Module for Gmail Organizer v2
==============================================
OAuth2 handling with encrypted credential storage.
"""

from __future__ import annotations

import json
import os
import pickle
import sys
import logging
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from .config import SCOPES
from .utils import C


_KEY_FILE = ".gmail_organizer_key"


def _get_or_create_key(key_path: Optional[str] = None) -> bytes:
    """Get or create a Fernet encryption key."""
    path = Path(key_path or _KEY_FILE)
    if path.exists():
        return path.read_bytes().strip()
    key = Fernet.generate_key()
    path.write_bytes(key)
    os.chmod(str(path), 0o600)
    return key


class GmailAuthenticator:
    """
    Handles OAuth2 authentication for Gmail API.
    Features encrypted token storage and automatic refresh.
    """

    def __init__(
        self,
        credentials_file: str = "credentials.json",
        token_file: str = "token.pickle",
        key_file: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self._key = _get_or_create_key(key_file)
        self.logger = logger or logging.getLogger(__name__)

    def authenticate(self) -> Credentials:
        """Authenticate via OAuth2. Returns valid Credentials."""
        creds = self._load_token()

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.info("Refreshing expired token...")
                try:
                    creds.refresh(Request())
                except Exception as e:
                    self.logger.warning(f"Token refresh failed: {e}")
                    creds = self._run_auth_flow()
            else:
                creds = self._run_auth_flow()
            self._save_token(creds)

        return creds

    def _load_token(self) -> Optional[Credentials]:
        """Load and decrypt stored token."""
        token_path = Path(self.token_file)
        if not token_path.exists():
            return None

        try:
            encrypted = token_path.read_bytes()
            f = Fernet(self._key)
            decrypted = f.decrypt(encrypted)
            token_data = json.loads(decrypted.decode("utf-8"))
            return Credentials.from_authorized_user_info(token_data, SCOPES)
        except Exception as e:
            self.logger.warning(f"Could not load encrypted token: {e}")
            # Try loading as pickle (migration from v1)
            try:
                with open(self.token_file, "rb") as fp:
                    creds = pickle.load(fp)
                self.logger.info("Migrated pickle token to encrypted storage")
                self._save_token(creds)
                return creds
            except Exception:
                return None

    def _save_token(self, creds: Credentials) -> None:
        """Encrypt and save token."""
        token_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": list(creds.scopes or SCOPES),
        }
        f = Fernet(self._key)
        encrypted = f.encrypt(json.dumps(token_data).encode("utf-8"))
        token_path = Path(self.token_file)
        token_path.write_bytes(encrypted)
        os.chmod(str(token_path), 0o600)
        self.logger.debug("Token saved (encrypted)")

    def _run_auth_flow(self) -> Credentials:
        """Run the OAuth2 authorization flow."""
        if not os.path.exists(self.credentials_file):
            print(
                f"\n{C.RED}{C.BOLD}[FATAL]{C.RESET} "
                f"'{self.credentials_file}' not found!"
            )
            sys.exit(1)

        self.logger.info("Starting OAuth2 authorization flow...")
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_file, SCOPES
        )
        creds = flow.run_local_server(port=0)
        self.logger.info("Authorization successful")
        return creds

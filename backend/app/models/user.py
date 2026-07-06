"""
FinSense AI — User Domain Model + Repository
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Optional

from app.config import settings
from app.core.exceptions import ConflictError, NotFoundError, StorageError
from app.core.logging import get_logger
from app.core.security import hash_password, verify_password

logger = get_logger(__name__)

_user_db_lock = Lock()
_USER_DB_PATH = Path("data/users.json")


class User:
    """User domain model."""

    __slots__ = ("id", "username", "password_hash", "display_name", "created_at")

    def __init__(
        self,
        username: str,
        password_hash: str,
        display_name: Optional[str] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.username = username
        self.password_hash = password_hash
        self.display_name = display_name or username
        self.created_at = created_at or datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "password_hash": self.password_hash,
            "display_name": self.display_name,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            id=data["id"],
            username=data["username"],
            password_hash=data["password_hash"],
            display_name=data.get("display_name"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
        )


class UserRepository:
    """JSON-file-backed user repository."""

    def __init__(self):
        self._path = _USER_DB_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def _read_all(self) -> dict[str, dict]:
        if not self._path.exists():
            return {}
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def _write_all(self, users: dict[str, dict]) -> None:
        tmp = self._path.with_suffix(".tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(users, f, default=str, indent=2)
            tmp.replace(self._path)
        except OSError as exc:
            raise StorageError(f"Failed to save users: {exc}")

    def create(self, username: str, password: str, display_name: Optional[str] = None) -> User:
        with _user_db_lock:
            users = self._read_all()
            if username in users:
                raise ConflictError(f"Username '{username}' is already taken.")
            user = User(
                username=username,
                password_hash=hash_password(password),
                display_name=display_name,
            )
            users[username] = user.to_dict()
            self._write_all(users)
        logger.info("Created user '%s' (id=%s)", username, user.id)
        return user

    def get_by_username(self, username: str) -> Optional[User]:
        users = self._read_all()
        data = users.get(username)
        if data is None:
            return None
        return User.from_dict(data)

    def get_by_id(self, user_id: str) -> Optional[User]:
        users = self._read_all()
        for data in users.values():
            if data.get("id") == user_id:
                return User.from_dict(data)
        return None

    def authenticate(self, username: str, password: str) -> User:
        user = self.get_by_username(username)
        if user is None or not verify_password(password, user.password_hash):
            raise NotFoundError("Invalid username or password.")
        return user


# Singleton
user_repository = UserRepository()

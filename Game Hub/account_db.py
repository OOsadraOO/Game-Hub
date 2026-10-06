# ==================================================
# GAMEHUB ACCOUNT DATABASE
# ==================================================

import hashlib
import hmac
import os
import secrets
import sqlite3
from datetime import datetime, timezone


DB_PATH = os.path.join("data", "accounts.db")
PBKDF2_ITERATIONS = 600_000


class AccountDB:
    """Local account storage for GameHub."""

    def __init__(self, db_path=DB_PATH):
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self.db_path = db_path
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self):
        with self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                    password_hash TEXT NOT NULL,
                    password_salt TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    last_used_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id INTEGER PRIMARY KEY,
                    remember_me INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

    @staticmethod
    def _now():
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _normalize_username(username):
        return " ".join(username.strip().split())

    @staticmethod
    def _validate_username(username):
        if not 3 <= len(username) <= 24:
            return False, "Username must be 3–24 characters."
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-")
        if any(char not in allowed for char in username):
            return False, "Username can use letters, numbers, _, -, and . only."
        return True, ""

    @staticmethod
    def _validate_password(password):
        if len(password) < 8:
            return False, "Password must be at least 8 characters."
        if len(password) > 128:
            return False, "Password is too long."
        if not any(char.isalpha() for char in password):
            return False, "Password must contain a letter."
        if not any(char.isdigit() for char in password):
            return False, "Password must contain a number."
        return True, ""

    @staticmethod
    def _hash_password(password, salt=None):
        salt_bytes = salt or os.urandom(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt_bytes,
            PBKDF2_ITERATIONS,
            dklen=32,
        )
        return salt_bytes.hex(), digest.hex()

    @staticmethod
    def _token_hash(token):
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def username_exists(self, username, exclude_user_id=None):
        username = self._normalize_username(username)
        with self._connect() as db:
            if exclude_user_id is None:
                row = db.execute(
                    "SELECT id FROM users WHERE username = ? COLLATE NOCASE",
                    (username,),
                ).fetchone()
            else:
                row = db.execute(
                    "SELECT id FROM users WHERE username = ? COLLATE NOCASE AND id != ?",
                    (username, exclude_user_id),
                ).fetchone()
        return row is not None

    def create_user(self, username, password):
        username = self._normalize_username(username)
        valid, message = self._validate_username(username)
        if not valid:
            return False, message, None

        valid, message = self._validate_password(password)
        if not valid:
            return False, message, None

        if self.username_exists(username):
            return False, "That username is already registered.", None

        salt, password_hash = self._hash_password(password)
        now = self._now()

        try:
            with self._connect() as db:
                cursor = db.execute(
                    """INSERT INTO users
                       (username, password_hash, password_salt, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?)""",
                    (username, password_hash, salt, now, now),
                )
                user_id = cursor.lastrowid
                db.execute(
                    "INSERT INTO user_preferences (user_id) VALUES (?)",
                    (user_id,),
                )
        except sqlite3.IntegrityError:
            return False, "That username is already registered.", None

        return True, "Account created successfully.", self.get_user(user_id)

    def authenticate(self, username, password):
        username = self._normalize_username(username)
        with self._connect() as db:
            row = db.execute(
                """SELECT id, username, password_hash, password_salt,
                          created_at, updated_at
                   FROM users WHERE username = ? COLLATE NOCASE""",
                (username,),
            ).fetchone()

        if row is None:
            return None

        salt = bytes.fromhex(row["password_salt"])
        _, candidate_hash = self._hash_password(password, salt=salt)
        if not hmac.compare_digest(candidate_hash, row["password_hash"]):
            return None

        return self.get_user(row["id"])

    def get_user(self, user_id):
        with self._connect() as db:
            row = db.execute(
                "SELECT id, username, created_at, updated_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        return dict(row) if row else None

    def change_username(self, user_id, new_username):
        new_username = self._normalize_username(new_username)
        valid, message = self._validate_username(new_username)
        if not valid:
            return False, message

        if self.username_exists(new_username, exclude_user_id=user_id):
            return False, "That username is already in use."

        with self._connect() as db:
            cursor = db.execute(
                "UPDATE users SET username = ?, updated_at = ? WHERE id = ?",
                (new_username, self._now(), user_id),
            )
        return (True, "Username updated.") if cursor.rowcount else (False, "Account not found.")

    def change_password(self, user_id, current_password, new_password):
        with self._connect() as db:
            row = db.execute(
                "SELECT password_hash, password_salt FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()

        if row is None:
            return False, "Account not found."

        salt = bytes.fromhex(row["password_salt"])
        _, candidate_hash = self._hash_password(current_password, salt=salt)
        if not hmac.compare_digest(candidate_hash, row["password_hash"]):
            return False, "Current password is incorrect."

        valid, message = self._validate_password(new_password)
        if not valid:
            return False, message

        new_salt, new_hash = self._hash_password(new_password)
        with self._connect() as db:
            db.execute(
                """UPDATE users
                   SET password_hash = ?, password_salt = ?, updated_at = ?
                   WHERE id = ?""",
                (new_hash, new_salt, self._now(), user_id),
            )
            db.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))

        return True, "Password updated. Please sign in again."

    def create_session(self, user_id):
        token = secrets.token_urlsafe(48)
        token_hash = self._token_hash(token)
        now = self._now()
        with self._connect() as db:
            db.execute(
                """INSERT INTO sessions
                   (user_id, token_hash, created_at, last_used_at)
                   VALUES (?, ?, ?, ?)""",
                (user_id, token_hash, now, now),
            )
        return token

    def get_user_by_token(self, token):
        if not token:
            return None
        token_hash = self._token_hash(token)
        with self._connect() as db:
            row = db.execute(
                """SELECT u.id, u.username, u.created_at, u.updated_at
                   FROM sessions s
                   JOIN users u ON u.id = s.user_id
                   WHERE s.token_hash = ?""",
                (token_hash,),
            ).fetchone()
            if row:
                db.execute(
                    "UPDATE sessions SET last_used_at = ? WHERE token_hash = ?",
                    (self._now(), token_hash),
                )
        return dict(row) if row else None

    def revoke_session(self, token):
        if not token:
            return
        with self._connect() as db:
            db.execute(
                "DELETE FROM sessions WHERE token_hash = ?",
                (self._token_hash(token),),
            )

    def delete_user(self, user_id):
        with self._connect() as db:
            cursor = db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return cursor.rowcount > 0

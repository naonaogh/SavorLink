from __future__ import annotations

import hashlib
import os


class AuthService:
    """
    MVP-хеширование пароля.
    В проде заменить на passlib/bcrypt/argon2 + proper salt storage.
    """

    def __init__(self, pepper: str | None = None) -> None:
        self.pepper = pepper or os.getenv("PASSWORD_PEPPER", "dev-pepper")

    def hash_password(self, password: str) -> str:
        data = (self.pepper + password).encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def verify_password(self, password: str, password_hash: str) -> bool:
        return self.hash_password(password) == password_hash


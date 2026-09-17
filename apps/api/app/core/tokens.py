from datetime import UTC, datetime, timedelta
from uuid import UUID

import bcrypt
import jwt

from app.core.config import Settings

ACCESS_COOKIE = "creatoros_access"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(user_id: UUID, settings: Settings) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_minutes)
    payload = {"sub": str(user_id), "exp": expire, "typ": "access"}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str, settings: Settings) -> UUID:
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    return UUID(str(payload["sub"]))

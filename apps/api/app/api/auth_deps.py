from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.tokens import ACCESS_COOKIE, decode_access_token
from app.db.models.domain import Creator
from app.db.models.user import User
from app.db.session import get_db


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(ACCESS_COOKIE)
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")
    try:
        user_id = decode_access_token(token, get_settings())
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session."
        ) from exc
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active.")
    return user


def get_current_creator(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Creator:
    creator = db.query(Creator).filter(Creator.user_id == user.id).one_or_none()
    if creator is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Creator profile not found."
        )
    return creator

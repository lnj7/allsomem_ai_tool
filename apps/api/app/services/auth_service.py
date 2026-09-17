from fastapi import HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.tokens import ACCESS_COOKIE, create_access_token, hash_password, verify_password
from app.db.models.domain import AutomationSettings, Creator
from app.db.models.user import User
from app.schemas.product import LoginRequest, RegisterRequest, UserOut


class AuthService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self._db = db
        self._settings = settings

    def register(self, payload: RegisterRequest, response: Response) -> UserOut:
        existing = self._db.query(User).filter(User.email == payload.email.lower()).one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered."
            )
        user = User(
            email=str(payload.email).lower(),
            password_hash=hash_password(payload.password),
            full_name=payload.full_name.strip(),
            is_active=True,
        )
        self._db.add(user)
        self._db.flush()
        creator = Creator(
            user_id=user.id, display_name=payload.full_name.strip(), onboarding_data={}
        )
        self._db.add(creator)
        self._db.flush()
        self._db.add(AutomationSettings(creator_id=creator.id, approval_mode="REVIEW_REQUIRED"))
        self._db.commit()
        self._db.refresh(user)
        self._set_cookie(response, user)
        return UserOut(
            id=user.id, email=user.email, full_name=user.full_name, is_active=user.is_active
        )

    def login(self, payload: LoginRequest, response: Response) -> UserOut:
        user = self._db.query(User).filter(User.email == payload.email.lower()).one_or_none()
        if (
            user is None
            or not user.password_hash
            or not verify_password(payload.password, user.password_hash)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password."
            )
        self._set_cookie(response, user)
        return UserOut(
            id=user.id, email=user.email, full_name=user.full_name, is_active=user.is_active
        )

    def logout(self, response: Response) -> None:
        response.delete_cookie(ACCESS_COOKIE)

    def _set_cookie(self, response: Response, user: User) -> None:
        token = create_access_token(user.id, self._settings)
        response.set_cookie(
            key=ACCESS_COOKIE,
            value=token,
            httponly=True,
            samesite="lax",
            secure=self._settings.is_production,
            max_age=self._settings.access_token_minutes * 60,
            path="/",
        )

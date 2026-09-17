from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.auth_deps import get_current_user
from app.core.config import get_settings
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.product import LoginRequest, RegisterRequest, UserOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db, get_settings())


@router.post("/register", response_model=UserOut)
def register(
    payload: RegisterRequest, response: Response, service: AuthService = Depends(_service)
) -> UserOut:
    return service.register(payload, response)


@router.post("/login", response_model=UserOut)
def login(
    payload: LoginRequest, response: Response, service: AuthService = Depends(_service)
) -> UserOut:
    return service.login(payload, response)


@router.post("/logout")
def logout(response: Response, service: AuthService = Depends(_service)) -> dict[str, str]:
    service.logout(response)
    return {"status": "ok"}


@router.post("/refresh", response_model=UserOut)
def refresh(
    response: Response,
    user: User = Depends(get_current_user),
    service: AuthService = Depends(_service),
) -> UserOut:
    service._set_cookie(response, user)
    return UserOut(id=user.id, email=user.email, full_name=user.full_name, is_active=user.is_active)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut(id=user.id, email=user.email, full_name=user.full_name, is_active=user.is_active)

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..deps import current_user
from ..models import AuditLog, User
from ..security import create_token, hash_password, verify_password

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email address")
        return v


class LoginIn(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    is_owner: bool


def log(db: Session, actor_id, event, detail=None):
    db.add(AuditLog(actor_id=actor_id, event_type=event, detail=detail))
    db.commit()


@router.post("/register", status_code=201)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    user_count = db.scalar(select(func.count()).select_from(User))
    if user_count > 0 and not settings.allow_registration:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Registration is closed")
    if db.scalar(select(User).where(User.email == body.email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    user = User(name=body.name, email=body.email,
                password_hash=hash_password(body.password), is_owner=(user_count == 0))
    db.add(user)
    db.commit()
    log(db, user.id, "user.registered")
    return {"token": create_token(user.id), "user": UserOut.model_validate(user, from_attributes=True)}


@router.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == body.email.strip().lower()))
    if not user or not user.is_active or not verify_password(body.password, user.password_hash):
        log(db, user.id if user else None, "auth.login_failed", body.email[:100])
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong email or password")
    log(db, user.id, "auth.login")
    return {"token": create_token(user.id), "user": UserOut.model_validate(user, from_attributes=True)}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user

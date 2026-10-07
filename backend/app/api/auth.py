
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.auth import RegisterRequest
from app.core.security import hash_password

from app.schemas.auth import LoginRequest, TokenResponse
from app.core.security import verify_password, create_access_token

from app.api.dependencies import get_current_user
from app.schemas.auth import UserResponse
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    # Public registration is only for students.
    # Counselor and admin accounts require separate provisioning.
    if data.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=403,
            detail="Only student self-registration is allowed",
        )

    existing_user = db.scalar(
        select(User).where(User.email == data.email.lower())
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    new_user = User(
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        display_name=data.display_name,
        university=data.university,
        role=UserRole.STUDENT,
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    except Exception:
        db.rollback()
        raise

    return {
        "message": "User registered successfully",
        "user_id": str(new_user.id),
        "email": new_user.email,
    }

@router.post("/login", response_model=TokenResponse)
def login_user(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(User.email == data.email.lower())
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "role": user.role.value,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user
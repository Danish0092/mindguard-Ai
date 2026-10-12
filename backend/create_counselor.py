
from getpass import getpass

from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.enums import UserRole
from app.models.user import User
from app.core.security import hash_password


def main():
    email = input("Counselor email: ").strip().lower()
    display_name = input("Counselor name: ").strip()
    university = input(
        "University (must match student): "
    ).strip()
    password = getpass("Counselor password: ")

    if not all([email, display_name, university, password]):
        print("All fields are required.")
        return

    db = SessionLocal()

    try:
        existing = db.scalar(
            select(User).where(User.email == email)
        )

        if existing:
            print("This email already exists. No account created.")
            return

        counselor = User(
            email=email,
            display_name=display_name,
            university=university,
            password_hash=hash_password(password),
            role=UserRole.COUNSELOR,
            is_active=True,
            is_on_call=True,
        )

        db.add(counselor)
        db.commit()
        db.refresh(counselor)

        print("Counselor account created successfully.")
        print("Email:", counselor.email)
        print("Role:", counselor.role.value)
        print("University:", counselor.university)
        print("On call:", counselor.is_on_call)

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

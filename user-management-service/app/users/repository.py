from datetime import datetime, timedelta, timezone
from typing import Optional

from .schemas import (
    ActivationCodeModel,
    UserModel,
    UserRegistrationModel,
    UserWithPasswordModal,
)
from .utils import generate_code, hash_password


def get_user_by_email(email: str, db, include_password: bool = False):
    with db.cursor() as cursor:
        if include_password:
            cursor.execute("SELECT * FROM users WHERE email = %s;", (email,))
        else:
            cursor.execute(
                "SELECT id, email, is_active FROM users WHERE email = %s;",
                (email,),
            )
        user = cursor.fetchone()
        if user:
            return (
                UserModel(**user)
                if not include_password
                else UserWithPasswordModal(**user)
            )
        return None


def create_user(user: UserRegistrationModel, db) -> Optional[UserModel]:
    password_hash = hash_password(user.password)
    with db.cursor() as cursor:
        cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id, email, is_active",
            (user.email, password_hash),
        )
        user = cursor.fetchone()
        db.commit()
        if user:
            return UserModel(**user)
        return None


def create_activation_code(user_id: int, db) -> str:
    code = generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=1)
    with db.cursor() as cursor:
        cursor.execute(
            "INSERT INTO activation_codes (user_id, code, expires_at) VALUES (%s, %s, %s);",
            (user_id, code, expires_at),
        )
        db.commit()
    return code


def get_activation_code(user_id: int, code: str, db) -> Optional[ActivationCodeModel]:
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM activation_codes WHERE user_id = %s AND code = %s;",
            (user_id, code),
        )
        code = cursor.fetchone()
        if code:
            return ActivationCodeModel(**code)
        return None


def activate_user(user_id: int, db) -> Optional[UserModel]:
    with db.cursor() as cursor:
        cursor.execute(
            "UPDATE users SET is_active = TRUE WHERE id = %s RETURNING id, email, is_active;",
            (user_id,),
        )
        user = cursor.fetchone()
        db.commit()
        if user:
            return UserModel(**user)
        return None

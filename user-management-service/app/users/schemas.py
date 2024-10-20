import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, validator
from pydantic.types import constr


class UserRegistrationModel(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class UserModel(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        orm_mode = True


class UserWithPasswordModal(UserModel):
    password_hash: str


class UserActivationModel(BaseModel):
    code: str

    @validator("code")
    def code_must_be_4_digits(cls, v):
        if not re.match(r"^\d{4}$", v):
            raise ValueError("Activation code must be exactly 4 digits")
        return v


class ActivationCodeModel(BaseModel):
    id: int
    user_id: int
    code: str
    expires_at: datetime

    class Config:
        orm_mode = True

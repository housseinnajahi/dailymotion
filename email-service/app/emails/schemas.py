import re

from pydantic import BaseModel, EmailStr, validator


class EmailRequest(BaseModel):
    email: EmailStr
    code: str

    @validator("code")
    def code_must_be_4_digits(cls, v):
        if not re.match(r"^\d{4}$", v):
            raise ValueError("Activation code must be exactly 4 digits")
        return v

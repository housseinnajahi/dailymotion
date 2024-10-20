from datetime import datetime, timezone
from typing import Annotated

import requests
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from ..config import email_service_settings
from ..postgres import postgres
from .repository import (
    activate_user,
    create_activation_code,
    create_user,
    get_activation_code,
    get_user_by_email,
)
from .schemas import UserActivationModel, UserModel, UserRegistrationModel
from .utils import verify_password

router = APIRouter(prefix="")
security = HTTPBasic()


@router.post(
    "/register",
    summary="Register a new user",
    description="Registers a user and sends an email containing the activation code.",
)
def register_user(
    user: UserRegistrationModel,
    db=Depends(postgres.get_db),
) -> UserModel:
    """
    Endpoint to register a new user.

    **Parameters**:
    - **user (UserRegistrationModel)**: The request body containing the user's email(must be unique) and password.

    On successful registration, the user will receive an activation code via email.

    **Returns**:
    - **UserModel**: The newly created user object.

    **Raises**:
    - **400 Bad Request**: If the user is already registered.
    - **403 Forbidden**: If the API key is invalid.
    - **500 Internal Server Error**: If an error occurs while sending the email.
    """

    existing_user = get_user_by_email(email=user.email, db=db)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )

    user = create_user(user=user, db=db)
    activation_code = create_activation_code(user_id=user.id, db=db)
    try:
        headers = {"x-api-key": email_service_settings.API_KEY}
        response = requests.post(
            email_service_settings.EMAIL_SERVICE_URL,
            headers=headers,
            json={"email": user.email, "code": activation_code},
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()["detail"]
            )
    except requests.exceptions.RequestException as e:
        raise e

    return user


@router.post(
    "/activate", summary="Activate a user", description="Activate a user account."
)
def activate_new_user(
    code: UserActivationModel,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    db=Depends(postgres.get_db),
):
    """
    Activate a user account.

    - **code (EmailRequest)**: The activation code sent to the user's email
    - **credentials (HTTPBasicCredentials)**: User's email and password

    On successful activation, the user's account will be marked as active.

    **Returns**:
    - User object.

    **Raises**:
    - **400 Bad Request**: If the user is already active or the activation code is invalid or expired.
    - **401 UNAUTHORIZED**: If the user's credentials are invalid.
    - **404 Not Found**: If the user does not exist.
    """
    user = get_user_by_email(email=credentials.username, db=db, include_password=True)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user and user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has already activated his account",
        )

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    activation_code = get_activation_code(user_id=user.id, code=code.code, db=db)
    if not activation_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid activation code"
        )
    if datetime.now(timezone.utc) > activation_code.expires_at.replace(
        tzinfo=timezone.utc
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Activation code has expired",
        )

    return activate_user(user_id=user.id, db=db)

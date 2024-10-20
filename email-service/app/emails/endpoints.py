import smtplib
from email.mime.text import MIMEText

from fastapi import APIRouter, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from ..config import email_server, smtp_settings
from .schemas import EmailRequest

router = APIRouter(prefix="")
header_scheme = APIKeyHeader(name="x-api-key")


@router.post(
    "/send",
    summary="Send Activation Email",
    description="Sends an activation email with the provided code.",
)
def send_email(
    email_request: EmailRequest, api_key_header: str = Security(header_scheme)
):
    """
    Endpoint to send an activation email to a user.

    **Parameters**:
    - **email_request (EmailRequest)**: The request body containing the user's email and activation code.
    - **api_key_header (str)**: API key to authenticate the request.

    **Returns**:
    - A success message when the email is sent successfully.

    **Raises**:
    - **403 Forbidden**: If the API key is invalid.
    - **500 Internal Server Error**: If an error occurs while sending the email.
    """
    print(api_key_header, email_server.api_key)
    if api_key_header != email_server.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden, you can't send email",
        )
    try:
        print(email_request)
        if smtp_settings.USE_SMTP:
            subject = "Activation Code"
            body = f"Your Activation code is: {email_request.code}"

            message = MIMEText(body, "plain")
            message["Subject"] = subject
            message["From"] = smtp_settings.SMTP_FROM
            message["To"] = email_request.email
            print(f"Your Activation code is: {email_request.code}")
            with smtplib.SMTP(
                smtp_settings.SMTP_SERVER, smtp_settings.SMTP_PORT
            ) as server:
                server.starttls()
                server.login(smtp_settings.SMTP_USERNAME, smtp_settings.SMTP_PASSWORD)
                server.sendmail(
                    smtp_settings.SMTP_FROM, email_request.email, message.as_string()
                )
        else:
            print(f"Your Activation code is: {email_request.code}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}",
        )
    return {"message": "Email sent successfully"}

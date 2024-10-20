from datetime import datetime

import psycopg2
from app.users.repository import get_user_by_email
from fastapi.security import HTTPBasicCredentials
from freezegun import freeze_time
from psycopg2.extras import RealDictCursor

from .conftest import MockPostgres

mock_postgres = MockPostgres()


def test_register_user(client, mock_post_request):
    user_data = {"email": "test@gmail.com", "password": "testtest"}
    response = client.post("api/v1/users/register", json=user_data)
    response_data = response.json()
    assert response.status_code == 200
    assert response_data["email"] == user_data["email"]
    assert response_data["is_active"] == False


def test_register_user_with_an_existing_email(client, mock_post_request):
    user_data = {"email": "test@gmail.com", "password": "testtest"}
    response = client.post("api/v1/users/register", json=user_data)
    response_data = response.json()
    assert response.status_code == 400
    assert response_data["detail"] == "User already exists"


def test_register_user_with_an_invalid_password(client, mock_post_request):
    user_data = {"email": "test1@gmail.com", "password": "test"}
    response = client.post("api/v1/users/register", json=user_data)
    response_data = response.json()
    assert response.status_code == 422
    assert (
        response_data["detail"][0]["msg"] == "String should have at least 8 characters"
    )


def test_register_user_with_an_invalid_email(client, mock_post_request):
    user_data = {"email": "test1gmail.com", "password": "testtest"}
    response = client.post("api/v1/users/register", json=user_data)
    response_data = response.json()
    assert response.status_code == 422
    assert (
        response_data["detail"][0]["msg"]
        == "value is not a valid email address: An email address must have an @-sign."
    )


def test_activate_user_not_exist(client, mock_post_request):
    user_data = {"email": "test-not-exist@gmail.com", "password": "testtest"}
    credentials = HTTPBasicCredentials(
        username=user_data["email"], password=user_data["password"]
    )
    activation_code = {"code": "0000"}

    response = client.post(
        "api/v1/users/activate",
        json=activation_code,
        auth=(credentials.username, credentials.password),
    )
    response_data = response.json()
    assert response.status_code == 404
    assert response_data["detail"] == "User not found"


def test_activate_user_with_wrong_credentials(client, mock_post_request):
    user_data = {"email": "test@gmail.com", "password": "tests"}
    activation_code = {"code": "0000"}
    credentials = HTTPBasicCredentials(
        username=user_data["email"], password=user_data["password"]
    )
    response = client.post(
        "api/v1/users/activate",
        json=activation_code,
        auth=(credentials.username, credentials.password),
    )
    response_data = response.json()
    assert response.status_code == 401
    assert response_data["detail"] == "Invalid credentials"


@freeze_time("2024-10-20 12:00:00")
def test_create_and_activate_user(client, mock_post_request):
    user_data = {"email": "test_1@gmail.com", "password": "testtest"}
    credentials = HTTPBasicCredentials(
        username=user_data["email"], password=user_data["password"]
    )

    response = client.post("api/v1/users/register", json=user_data)
    response_data = response.json()
    assert response_data["is_active"] == False

    with psycopg2.connect(
        mock_postgres.database_url, cursor_factory=RealDictCursor
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM activation_codes WHERE user_id = %s;",
                (response_data["id"],),
            )
            code = cursor.fetchone()
    activation_code = {"code": code["code"]}

    response = client.post(
        "api/v1/users/activate",
        json=activation_code,
        auth=(credentials.username, credentials.password),
    )
    response_data = response.json()
    assert response.status_code == 200
    assert response_data["is_active"] == True


@freeze_time("2024-10-20 12:00:00")
def test_create_and_activate_user_with_wrong_code(client, mock_post_request):
    user_data = {"email": "test_2@gmail.com", "password": "testtest"}
    credentials = HTTPBasicCredentials(
        username=user_data["email"], password=user_data["password"]
    )

    response = client.post("api/v1/users/register", json=user_data)
    response_data = response.json()
    assert response_data["is_active"] == False

    with psycopg2.connect(
        mock_postgres.database_url, cursor_factory=RealDictCursor
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM activation_codes WHERE user_id = %s;",
                (response_data["id"],),
            )
            code = cursor.fetchone()
    activation_code = {"code": "0000" if code["code"] != "0000" else "0001"}

    response = client.post(
        "api/v1/users/activate",
        json=activation_code,
        auth=(credentials.username, credentials.password),
    )
    response_data = response.json()
    assert response.status_code == 400
    assert response_data["detail"] == "Invalid activation code"


@freeze_time("2024-10-20 12:00:00")
def test_activate_user_an_active_user(client, mock_post_request):
    user_data = {"email": "test_1@gmail.com", "password": "testtest"}
    credentials = HTTPBasicCredentials(
        username=user_data["email"], password=user_data["password"]
    )

    with psycopg2.connect(
        mock_postgres.database_url, cursor_factory=RealDictCursor
    ) as connection:
        user = get_user_by_email(email=user_data["email"], db=connection)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM activation_codes WHERE user_id = %s;",
                (user.id,),
            )
            code = cursor.fetchone()
    activation_code = {"code": code["code"]}

    response = client.post(
        "api/v1/users/activate",
        json=activation_code,
        auth=(credentials.username, credentials.password),
    )
    response_data = response.json()
    assert response.status_code == 400
    assert response_data["detail"] == "User has already activated his account"


@freeze_time("2024-10-20 12:00:00")
def test_create_and_activate_user_after_code_expiration(client, mock_post_request):
    user_data = {"email": "test_3@gmail.com", "password": "testtest"}
    credentials = HTTPBasicCredentials(
        username=user_data["email"], password=user_data["password"]
    )

    response = client.post("api/v1/users/register", json=user_data)
    response_data = response.json()
    assert response_data["is_active"] == False

    with psycopg2.connect(
        mock_postgres.database_url, cursor_factory=RealDictCursor
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM activation_codes WHERE user_id = %s;",
                (response_data["id"],),
            )
            code = cursor.fetchone()
    activation_code = {"code": code["code"]}
    with freeze_time("2024-10-20 12:02:00"):
        response = client.post(
            "api/v1/users/activate",
            json=activation_code,
            auth=(credentials.username, credentials.password),
        )
        response_data = response.json()
        assert response.status_code == 400
        assert response_data["detail"] == "Activation code has expired"

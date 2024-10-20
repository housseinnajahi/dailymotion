import psycopg2
import pytest
import requests
from app.config import postgres_settings
from app.main import app
from app.postgres import postgres
from fastapi.testclient import TestClient
from psycopg2.extras import RealDictCursor


@pytest.fixture
def mock_post_request(monkeypatch):
    class MockResponse:
        def __init__(self, status_code):
            self.status_code = status_code

        def json(self):
            return {"message": "Email sent successfully"}

    def mock_post_request(url, headers=None, json=None):
        return MockResponse(status_code=200)

    monkeypatch.setattr(requests, "post", mock_post_request)


class MockPostgres:
    def __init__(self):
        self.database_url = f"postgresql://{postgres_settings.POSTGRES_USER}:{postgres_settings.POSTGRES_PASSWORD}@postgres-db/{postgres_settings.POSTGRES_DB}_test"
        self.init_database()

    def get_db(self):
        connection = psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
        try:
            yield connection
        finally:
            connection.close()

    def init_database(self):
        with psycopg2.connect(
            self.database_url, cursor_factory=RealDictCursor
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS activation_codes;")
                cursor.execute("DROP TABLE IF EXISTS users;")
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        is_active BOOLEAN DEFAULT FALSE
                    );
                    
                    CREATE TABLE IF NOT EXISTS activation_codes (
                        id SERIAL PRIMARY KEY,
                        user_id INT REFERENCES users(id) ON DELETE CASCADE,
                        code VARCHAR(4) NOT NULL,
                        expires_at TIMESTAMP NOT NULL
                    );
                """
                )
                connection.commit()


mock_postgres = MockPostgres()


@pytest.fixture
def client():
    app.dependency_overrides[postgres.get_db] = mock_postgres.get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides = {}

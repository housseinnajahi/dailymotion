import psycopg2
from psycopg2.extras import RealDictCursor

from .config import postgres_settings


class Postgres:
    def __init__(self):
        self.database_url = f"postgresql://{postgres_settings.POSTGRES_USER}:{postgres_settings.POSTGRES_PASSWORD}@postgres-db/{postgres_settings.POSTGRES_DB}"

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


postgres = Postgres()

import os

from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """Database configuration model with validation."""

    host: str = Field(default="localhost", description="MySQL host")
    port: int = Field(default=3306, description="MySQL port")
    user: str = Field(description="MySQL username")
    password: str = Field(description="MySQL password")
    database: str = Field(description="MySQL database name")
    charset: str = Field(default="utf8mb4", description="MySQL charset")
    collation: str = Field(default="utf8mb4_unicode_ci", description="MySQL collation")
    autocommit: bool = Field(default=True, description="Auto-commit mode")
    sql_mode: str = Field(default="TRADITIONAL", description="SQL mode")
    connection_timeout: int = Field(
        default=10, description="Connection timeout in seconds"
    )
    pool_size: int = Field(default=5, description="Connection pool size")
    pool_reset_session: bool = Field(
        default=True, description="Reset session on connection return"
    )

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Create DatabaseConfig from environment variables with validation."""
        user = os.getenv("MYSQL_USER")
        password = os.getenv("MYSQL_PASSWORD")
        database = os.getenv("MYSQL_DATABASE")

        if not all([user, password, database]):
            raise ValueError(
                "Missing required database configuration: MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DATABASE are required"
            )

        # At this point, we know user, password, and database are not None
        assert user is not None
        assert password is not None
        assert database is not None

        return cls(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=user,
            password=password,
            database=database,
            charset=os.getenv("MYSQL_CHARSET", "utf8mb4"),
            collation=os.getenv("MYSQL_COLLATION", "utf8mb4_unicode_ci"),
            autocommit=os.getenv("MYSQL_AUTOCOMMIT", "true").lower() == "true",
            sql_mode=os.getenv("MYSQL_SQL_MODE", "TRADITIONAL"),
            connection_timeout=int(os.getenv("MYSQL_CONNECTION_TIMEOUT", "10")),
            pool_size=int(os.getenv("MYSQL_POOL_SIZE", "5")),
            pool_reset_session=os.getenv("MYSQL_POOL_RESET_SESSION", "true").lower()
            == "true",
        )

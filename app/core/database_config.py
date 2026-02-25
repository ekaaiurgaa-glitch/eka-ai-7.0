"""PostgreSQL Production Configuration - TDD Section 2.2"""
import os


class DatabaseConfig:
    """Database configuration enforcing PostgreSQL in production"""
    
    @staticmethod
    def get_database_url() -> str:
        env = os.getenv("ENVIRONMENT", "development")
        
        if env == "production":
            # Enforce PostgreSQL in production
            db_url = os.getenv("DATABASE_URL")
            if not db_url or not db_url.startswith("postgresql"):
                raise ValueError(
                    "TDD Violation: Production MUST use PostgreSQL 16. "
                    "Set DATABASE_URL=postgresql://..."
                )
            return db_url
        
        elif env == "staging":
            # Staging should also use PostgreSQL
            db_url = os.getenv("DATABASE_URL", "postgresql://localhost/eka_ai_staging")
            if not db_url.startswith("postgresql"):
                raise ValueError("Staging MUST use PostgreSQL")
            return db_url
        
        else:
            # Development can use SQLite
            return os.getenv("DATABASE_URL", "sqlite:///./eka_ai.db")
    
    @staticmethod
    def validate_postgresql_version(connection):
        """Ensure PostgreSQL 16 as per TDD Section 2.2"""
        result = connection.execute("SELECT version()")
        version_string = result.scalar()
        
        if "PostgreSQL 16" not in version_string:
            raise ValueError(
                f"TDD Violation: Requires PostgreSQL 16. Found: {version_string}"
            )


# Usage in config.py
def get_validated_database_url():
    return DatabaseConfig.get_database_url()

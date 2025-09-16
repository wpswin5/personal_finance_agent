from functools import lru_cache

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Settings for the FastAPI server.
    Based on pydantic BaseSettings - powerful tool autoload the .env file in the background.
    """
    
    # AUTH0 configuration    
    AUTH0_DOMAIN: str
    AUTH0_ALGORITHMS: str = "RS256"
    AUTH0_DEFAULT_DB_CONNECTION: str = "Username-Password-Authentication"
    AUTH0_API_DEFAULT_AUDIENCE: str
    AUTH0_APPLICATION_CLIENT_ID: str
    AUTH0_APPLICATION_CLIENT_SECRET: str
    #AUTH0_TEST_USERNAME: str
    #AUTH0_TEST_PASSWORD: str
    
    #AUTH0_MANAGEMENT_API_CLIENT_ID: str
    #AUTH0_MANAGEMENT_API_CLIENT_SECRET: str
    #AUTH0_MANAGEMENT_API_AUDIENCE: str
    
    # Plaid configuration
    PLAID_CLIENT_ID: str
    PLAID_SECRET: str
    PLAID_ENV: str = "sandbox"  # sandbox, development, or production
    
    # Encryption key for sensitive data
    ENCRYPTION_KEY: str = "your-32-byte-encryption-key-here"  # Should be 32 bytes for AES-256

    class Config:
        """
        Tell BaseSettings the env file path
        """

        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """
    Get settings. ready for FastAPI's Depends.
    lru_cache - cache the Settings object per arguments given.
    """
    settings = Settings()
    return settings
"""
Environment configuration management.

This module handles loading and validating environment variables from .env file.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for managing environment variables."""

    # OpenAI API Key (currently not used, but defined for future LLM features)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    @classmethod
    def validate(cls):
        """
        Validate required environment variables.

        Returns:
            tuple: (is_valid, list of missing variables)
        """
        missing = []

        # Currently no required variables, but this structure is ready for future requirements
        # Example for future:
        # if not cls.OPENAI_API_KEY:
        #     missing.append("OPENAI_API_KEY")

        return len(missing) == 0, missing

    @classmethod
    def get_api_key(cls):
        """
        Get OpenAI API key with validation.

        Returns:
            str: API key if available and valid
            None: If API key is not set or invalid

        Example:
            >>> api_key = Config.get_api_key()
            >>> if api_key:
            >>>     # Use the API key
            >>>     pass
        """
        key = cls.OPENAI_API_KEY

        if not key:
            return None

        # Basic validation
        if len(key) < 20:  # OpenAI keys are typically longer
            return None

        return key

    @classmethod
    def is_production(cls):
        """
        Check if running in production environment.

        Returns:
            bool: True if in production, False otherwise
        """
        env = os.getenv("ENVIRONMENT", "development").lower()
        return env == "production"

    @classmethod
    def get_debug_mode(cls):
        """
        Check if debug mode is enabled.

        Returns:
            bool: True if debug mode enabled, False otherwise
        """
        debug = os.getenv("DEBUG", "false").lower()
        return debug in ("true", "1", "yes")

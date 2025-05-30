from groq import AsyncGroq

from app.core.config import settings


class GroqClientSingleton:
    """
    Singleton class for managing an asynchronous Groq client.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            try:
                cls._instance = AsyncGroq(api_key=settings.GROQ_API_KEY)
            except Exception as e:
                raise RuntimeError(f"Error initializing Groq client: {str(e)}") from e
        return cls._instance


def get_groq_async_client():
    """
    Get a singleton instance of the asynchronous Groq client.

    Returns
    -------
    AsyncGroq
        An asynchronous Groq client instance.
    """
    return GroqClientSingleton()

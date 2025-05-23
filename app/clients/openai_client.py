import openai

from app.core.config import settings


class OpenAIClientSingleton:
    """
    Singleton class for managing an asynchronous OpenAI client.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            try:
                cls._instance = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                raise RuntimeError(f"Error initializing OpenAI client: {str(e)}")
        return cls._instance


def get_openai_async_client():
    """
    Get a singleton instance of the asynchronous OpenAI client.

    Returns
    -------
    openai.AsyncOpenAI
        An asynchronous OpenAI client instance.
    """
    return OpenAIClientSingleton()

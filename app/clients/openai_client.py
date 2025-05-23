import openai

from app.core.config import settings

_openai_async_client = None


def get_openai_async_client():
    """
    Get a singleton instance of the asynchronous OpenAI client.

    Returns
    -------
    openai.AsyncOpenAI
        An asynchronous OpenAI client instance.
    """
    global _openai_async_client

    if _openai_async_client is None:
        _openai_async_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    return _openai_async_client

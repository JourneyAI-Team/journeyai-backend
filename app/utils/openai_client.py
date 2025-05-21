import openai

from app.core.config import settings

_openai_async_client = None


def get_openai_async_client():
    global _openai_async_client
    _openai_async_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_async_client

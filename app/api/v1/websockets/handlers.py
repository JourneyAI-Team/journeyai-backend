from typing import Any

from app.utils.websocket.handlers import register_handler


@register_handler("ingest_message")
async def ingest_message(connection_id: str, data: dict[str, Any]):
    pass

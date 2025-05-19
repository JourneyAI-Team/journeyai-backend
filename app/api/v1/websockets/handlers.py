from typing import Any

from app.models.user import User
from app.utils.websocket.handlers import register_handler


@register_handler("ingest_message")
async def ingest_message(connection_id: str, user: User, data: dict[str, Any]):
    # NOTE: temporary user print to check if event is called
    print(user)
    pass

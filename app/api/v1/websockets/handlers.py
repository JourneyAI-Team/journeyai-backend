from typing import Any

from app.models.user import User
from app.models.message import Message


from app.utils.websocket.handlers import register_handler


@register_handler("ingest_message")
async def ingest_message(connection_id: str, user: User, data: dict[str, Any]):

    new_user_message = Message(
        sender="user",
        input={"content": data["content"], "attachments": data["attachments"]},
        assistant_id=data["assistant_id"],
        session_id=data["session_id"],
        organization_id=user.organization_id,
        user_id=user.id,
        output=None,
    )

    await new_user_message.insert()

    pass

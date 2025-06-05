import json

from app.models.message import Message
from app.models.session import Session
from app.models.user import User
from app.schemas.types import SenderType
from app.utils.misc_utils import format_datetime_to_string


def construct_embedding_input_for_artifact(title: str, body: str, source: str):
    embedding_input = f"""
    Title: {title}
    Body: {body}
    """
    if source == "user":
        embedding_input = (
            """
        Uploaded by User
        """
            + embedding_input
        )
    return embedding_input


async def construct_embedding_input_for_message(message: Message):

    session = await Session.get(message.session_id)
    user = await User.get(message.user_id)

    if message.sender == SenderType.USER:
        embedding_input = f"""
# User Message
Session Details: 
    - Title: {session.title}
User's Details:
    - Email: {user.email}
Message Details:
    - ID: {message.id}
    - Content: {message.content}
    - Created At: {format_datetime_to_string(message.created_at)}
"""

        return embedding_input
    else:
        embedding_input = f"""
# Assistant Message
Session Details: 
    - Title: {session.title}
User's Details:
    - Email: {user.email}
Raw Message Dump:
```json
{json.dumps(message.output, indent=2)}
```
"""

    return embedding_input

from openai.types.responses.response_input_item_param import ResponseInputItemParam

from app.models.assistant import Assistant
from app.models.message import Message
from app.models.session import Session
from app.schemas.types import SenderType


async def get_objects_from_session(session_id: str) -> tuple[Session, Assistant]:
    """
    Retrieve the Session and Assistant objects associated with a given session ID.

    Parameters
    ----------
    session_id : str
        The unique identifier for the session.

    Returns
    -------
    tuple[Session, Assistant]
        A tuple containing the Session and Assistant objects.

    Raises
    ------
    ValueError
        If the session or assistant cannot be found.
    """
    session = await Session.get(session_id)
    if not session:
        raise ValueError(f"Session not found: {session_id}")

    assistant = await Assistant.get(session.assistant_id)
    if not assistant:
        raise ValueError(f"Assistant not found: {session.assistant_id}")

    return session, assistant


async def fetch_message_history(session_id: str, limit: int = 100) -> list[Message]:
    """
    Fetch the last `limit` messages from the message history of a given session.

    Parameters
    ----------
    session_id : str
        The unique identifier for the session.
    limit : int, optional
        The maximum number of messages to fetch. Defaults to 100.

    Returns
    -------
    list[Message]
        A list of Message objects.
    """
    messages = (
        await Message.find(Message.session_id == session_id)
        .sort("-created_at")
        .limit(limit)
        .to_list()
    )
    return list(reversed(messages))


def convert_messages_to_openai_format(
    messages: list[Message],
) -> list[ResponseInputItemParam]:
    """
    Convert a list of Message objects to a list of OpenAI response input item parameters.

    Parameters
    ----------
    messages : list[Message]
        A list of Message objects.

    Returns
    -------
    list[ResponseInputItemParam]
        A list of OpenAI response input item parameters.
    """

    openai_messages = []

    for message in messages:
        if message.sender == SenderType.USER and message.input:
            openai_messages.append(
                {
                    "role": "user",
                    **message.input,
                }
            )
        elif message.sender == SenderType.ASSISTANT and message.output:
            openai_messages.append(message.output)

    return openai_messages

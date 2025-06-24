from loguru import logger

from app.clients.groq_client import get_groq_async_client
from app.clients.openai_client import get_openai_async_client
from app.core.config import settings
from app.models.message import Message
from app.models.session import Session
from app.schemas.types import SenderType


async def check_and_title_session(ctx, session_id: str):
    """
    Check if a session should be automatically titled and do so if needed.

    This task is triggered after each user message. It counts the number of
    user messages in the session, and if exactly 2 user messages exist,
    it generates a concise title based on those messages and updates the session.

    Parameters
    ----------
    session_id : str
        The ID of the session to check and potentially title.
    """
    session = await Session.get(session_id)
    if not session:
        logger.warning(f"Session not found for ID: {session_id}")
        return

    with logger.contextualize(
        session_id=session.id,
        user_id=session.user_id,
        organization_id=session.organization_id,
        assistant_id=session.assistant_id,
        account_id=session.account_id,
    ):
        # Skip if session already has a custom title (not the default)
        if session.title != "New Session":
            logger.debug("Session already has a custom title, skipping auto-titling")
            return

        # Count user messages in the session
        user_messages = await Message.find(
            Message.session_id == session_id, Message.sender == SenderType.USER
        ).to_list()

        user_message_count = len(user_messages)
        logger.debug(f"Found {user_message_count} user messages in session")

        # Only auto-title when there are exactly 2 user messages
        if user_message_count != 2:
            logger.debug(
                f"Session has {user_message_count} user messages, not titling yet"
            )
            return

        logger.info("Session has exactly 2 user messages, generating title...")

        # Get the first 2 user messages for context
        first_two_messages = sorted(user_messages, key=lambda m: m.created_at)[:2]

        # Generate title using AI service
        try:
            title = await _generate_session_title(first_two_messages)

            # Update session title
            session.title = title
            await session.save()

            logger.success(f"Successfully updated session title to: '{title}'")

        except Exception as e:
            logger.error(f"Failed to generate or update session title: {str(e)}")


async def _generate_session_title(messages: list[Message]) -> str:
    """
    Generate a concise title for a session based on the first 2 user messages.

    Parameters
    ----------
    messages : list[Message]
        List of user messages to base the title on (should be first 2 messages).

    Returns
    -------
    str
        A concise session title (3-6 words).
    """
    # Extract content from messages
    message_contents = []
    for msg in messages:
        if msg.input and msg.input.get("content"):
            message_contents.append(msg.input["content"])

    if not message_contents:
        return "New Session"

    # Create prompt for title generation
    messages_text = "\n\n".join(
        [f"Message {i+1}: {content}" for i, content in enumerate(message_contents)]
    )

    llm_input = [
        {
            "role": "system",
            "content": "You are a helpful assistant that creates concise, descriptive titles for chat sessions. Based on the user's first messages, generate a title that captures the main topic or purpose. The title should be 3-6 words, professional, and descriptive. Do not use quotes or special formatting.",
        },
        {
            "role": "user",
            "content": f"Please create a concise title for this chat session based on these first messages:\n\n{messages_text}\n\nTitle:",
        },
    ]

    logger.debug("Generating session title using AI service")

    try:
        if settings.GROQ_API_KEY:
            client = get_groq_async_client()
            chat_completion = await client.chat.completions.create(
                model="llama3-8b-8192",
                messages=llm_input,
                max_tokens=20,
                temperature=0.3,
            )
            title = chat_completion.choices[0].message.content.strip()

        elif settings.OPENAI_API_KEY:
            client = get_openai_async_client()
            response = await client.responses.create(
                input=llm_input,
                model="chatgpt-4o-latest",
                max_output_tokens=20,
                temperature=0.3,
            )
            title = response.output_text.strip()

        else:
            logger.warning("No LLM provider configured, using fallback title")
            # Fallback: create title from first few words of first message
            first_message = message_contents[0]
            words = first_message.split()[:4]
            title = " ".join(words)
            if len(first_message.split()) > 4:
                title += "..."

        # Clean up the title
        title = title.strip().strip('"').strip("'")

        # Ensure title is reasonable length
        if len(title) > 50:
            title = title[:47] + "..."

        # Fallback if title is empty
        if not title:
            title = "New Session"

        logger.debug(f"Generated title: '{title}'")
        return title

    except Exception as e:
        logger.error(f"Error generating title with AI service: {str(e)}")
        # Fallback: create title from first few words of first message
        if message_contents:
            first_message = message_contents[0]
            words = first_message.split()[:4]
            title = " ".join(words)
            if len(first_message.split()) > 4:
                title += "..."
            return title
        return "New Session"

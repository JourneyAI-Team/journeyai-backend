from typing import Callable

from agents import RunContextWrapper, function_tool

from app.clients.arq_client import get_arq
from app.models.artifact import Artifact
from app.schemas.agent_context import AgentContext
from app.schemas.types import OriginType


@function_tool
async def save_artifact(
    wrapper: RunContextWrapper[AgentContext], artifact_type: str, title: str, body: str
):
    """**CRITICAL FOR MEMORY RETENTION** - This is your ONLY way to remember information across conversations!

    Without using this tool, ALL information from this conversation will be permanently lost when the chat ends.
    You MUST save important details, insights, preferences, context, and any information you'll need to reference
    in future conversations. This is not optional - it's essential for providing continuity and personalized
    assistance to the user.

    Use this tool proactively and frequently throughout conversations to:
    - Save user preferences, goals, and context
    - Record important insights or discoveries
    - Store key information that builds over time
    - Maintain continuity across chat sessions

    Think of this as your external memory - use it liberally to ensure nothing important is forgotten.

    Args:
        artifact_type (str): The type of artifact to save. It should be a programmatic string
            that describes the type of artifact. (e.g., "person", "location", etc.)
        title: The title of the artifact.
        body: The body of the artifact.
    """

    arq = await get_arq()

    new_artifact = Artifact(
        type=artifact_type,
        title=title,
        body=body,
        origin_type=OriginType.LLM,
        user_id=wrapper.context.user.id,
        organization_id=wrapper.context.organization.id,
        account_id=wrapper.context.account.id,
        session_id=wrapper.context.session.id,
    )
    await new_artifact.insert()
    await arq.enqueue_job(
        "post_artifact_creation", new_artifact.id, _queue_name="artifacts"
    )


def get_tool() -> Callable:
    return save_artifact

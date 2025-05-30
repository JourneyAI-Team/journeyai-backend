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
    """Save an artifact to your memory. Think of artifacts as notes or highlights from
    the conversation you are having with the user. It is highly recommended to frequently
    take notes to enrich your memory.

    Args:
        artifact_type: The type of artifact to save. It should be a programmatic string
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

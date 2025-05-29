from typing import Callable

from agents import function_tool

from app.clients.arq_client import get_arq
from app.models.artifact import Artifact
from app.schemas.types import OriginType


# TODO: provide a proper description
@function_tool
async def save_artifact(
    artifact_type: str, title: str, body: str, origin_type: OriginType = "llm"
):
    """ """
    arq = await get_arq()

    new_artifact = Artifact(
        type=artifact_type, title=title, body=body, origin_type=origin_type
    )
    await new_artifact.insert()
    await arq.enqueue_job(
        "post_artifact_creation", new_artifact.id, _queue_name="artifacts"
    )


def get_tool() -> Callable:
    return save_artifact

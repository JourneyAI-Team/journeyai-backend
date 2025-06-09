import datetime as dt
import uuid

from beanie import Document
from pydantic import Field
from typing_extensions import NotRequired, TypedDict

from app.schemas.types import ToolType


class AssistantTool(TypedDict):
    name: str
    type: ToolType


class AssistantToolConfig(TypedDict):
    tools: NotRequired[list[AssistantTool]]
    vector_store_ids: NotRequired[list[str]]


class Assistant(Document):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)

    name: str
    internal_name: str
    description: str

    tool_config: AssistantToolConfig = Field(default_factory=AssistantToolConfig)
    testing: bool = False
    version: str = "0.0.1"

    # Agent Parameters
    developer_prompt: str
    model: str = "gpt-4o"

    created_at: dt.datetime = Field(
        default_factory=lambda: dt.datetime.now(dt.timezone.utc)
    )

import datetime as dt

from pydantic import BaseModel

from app.models.assistant import AssistantToolConfig
from app.schemas.types import AssistantCategoryType, ToolType


class AssistantBase(BaseModel):
    """
    Assistant base schema with common attributes
    """

    name: str
    internal_name: str
    description: str
    category: str = "General"
    tool_config: AssistantToolConfig = {
        "tools": [
            {
                "name": "save_artifact",
                "type": ToolType.INTERNAL,
            },
            {
                "name": "search_artifacts",
                "type": ToolType.INTERNAL,
            },
            {
                "name": "openai_web_search",
                "type": ToolType.EXTERNAL,
            },
        ]
    }
    testing: bool = False
    version: str = "0.0.1"
    developer_prompt: str
    model: str = "o3-mini"


class AssistantCreate(AssistantBase):
    """
    Schema for creating an assistant.
    """


class AssistantUpdate(BaseModel):
    """
    Schema for updating an assistant.
    """

    name: str | None = None
    internal_name: str | None = None
    description: str | None = None
    category: str | None = None
    tool_config: dict[str, str] | None = None
    testing: bool | None = None
    version: str | None = None
    developer_prompt: str | None = None
    model: str | None = None


class AssistantRead(AssistantBase):
    """
    Schema for reading an assistant.
    """

    id: str
    created_at: dt.datetime

class AssistantCategoryRead(BaseModel):
    """
    Schema for reading an assistant category.
    """

    assistant_categories: list[AssistantCategoryType]
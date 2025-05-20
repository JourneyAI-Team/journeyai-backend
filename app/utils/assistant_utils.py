import importlib

from agents import Agent

from app.models.assistant import Assistant
from app.schemas.agent_context import AgentContext
from app.schemas.types import ToolType


def get_agent_from_assistant(assistant: Assistant) -> Agent:
    return Agent[AgentContext](
        name=assistant.name,
        model=assistant.model,
        instructions=assistant.developer_prompt,  # TODO Support dynamic instructions such as pulling Artifact context
    )


def get_tool(
    tool_name: str,
    type: ToolType,
):
    module = importlib.import_module(f"app.tools.{type}.{tool_name}")
    return module.get_tool()

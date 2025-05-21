from agents import Agent

from app.models.assistant import Assistant
from app.schemas.agent_context import AgentContext


def get_agent_from_assistant(assistant: Assistant) -> Agent:
    return Agent[AgentContext](
        name=assistant.name,
        model=assistant.model,
        instructions=assistant.developer_prompt,  # TODO Support dynamic instructions such as pulling Artifact context
    )

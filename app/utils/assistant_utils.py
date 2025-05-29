from agents import Agent

from app.models.assistant import Assistant
from app.schemas.agent_context import AgentContext
from app.tools.internal.save_artifact import save_artifact


def get_agent_from_assistant(assistant: Assistant) -> Agent:

    return Agent[AgentContext](
        name=assistant.name,
        model=assistant.model,
        tools=[
            save_artifact,
        ],
        instructions=assistant.developer_prompt,  # TODO Support dynamic instructions such as pulling Artifact context
    )

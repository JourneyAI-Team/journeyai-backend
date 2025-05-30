from agents import Agent, WebSearchTool

from app.models.assistant import Assistant
from app.schemas.agent_context import AgentContext
from app.utils.tool_utils import get_tool


def get_agent_from_assistant(assistant: Assistant) -> Agent:

    # Retrieve tools
    tools = []
    for tool in assistant.tool_config["tools"]:
        match tool["name"]:
            case "openai_web_search":
                tools.append(WebSearchTool())
            case _:
                tools.append(get_tool(tool["name"], tool["type"]))

    return Agent[AgentContext](
        name=assistant.name,
        model=assistant.model,
        tools=tools,
        instructions=assistant.developer_prompt,  # TODO Support dynamic instructions such as pulling Artifact context
    )

import importlib

from app.schemas.types import ToolType


def get_tool(
    tool_name: str,
    type: ToolType,
):
    module = importlib.import_module(f"app.tools.{type}.{tool_name}")
    return module.get_tool()

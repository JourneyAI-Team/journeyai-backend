from app.core.config import settings


def get_mcp_server_params():
    return {
        "command": "npx",
        "args": ["-y", "search1api-mcp"],
        "env": {"SEARCH1API_KEY": settings.SEARCH1_API_KEY},
    }

def get_mcp_server_params():
    return {
        "command": "npx",
        "args": ["-y", "search1api-mcp"],
        "env": {"SEARCH1API_KEY": "AC512ABC-A9E7-4CEA-8773-0EC1D5092208"},
    }

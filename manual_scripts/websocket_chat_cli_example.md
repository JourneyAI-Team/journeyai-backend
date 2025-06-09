# WebSocket Chat CLI Usage

## Prerequisites

First, install the new dependency:
```bash
poetry install
```

## Basic Usage

Run the CLI with a session ID:
```bash
python manual_scripts/websocket_chat_cli.py 4fe513ff6cef4687bb6ef184342d2c2d
```

## Advanced Usage

Override the WebSocket URL or API key:
```bash
python manual_scripts/websocket_chat_cli.py 4fe513ff6cef4687bb6ef184342d2c2d --ws-url ws://localhost:8000/api/v1 --api-key your_api_key
```

## What You'll See

The CLI will display:
- **Green panels**: Assistant messages
- **Yellow panels**: Tool calls (with emojis 🔧)
- **Cyan panels**: Tool outputs
- **Magenta panels**: Agent switches (🤖)
- **Blue panels**: Agent handoffs (🔄)
- **Real-time streaming**: Text appears as it's being generated

## Commands

- Type any message and press Enter to send
- Type `quit` or `exit` to leave
- Press `Ctrl+C` to force quit

## Features

- Real-time streaming text display
- Formatted tool calls and outputs
- Agent switch notifications
- Graceful error handling
- Beautiful colored output using Rich library
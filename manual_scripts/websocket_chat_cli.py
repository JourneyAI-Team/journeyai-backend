#!/usr/bin/env python
import argparse
import asyncio
import json
import signal
import sys
from typing import Any, Dict

import websockets
from rich import print as rprint
from rich.console import Console
from rich.json import JSON
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

# Configuration
WS_BASE_URL = "ws://0.0.0.0:8000/api/v1"
API_KEY = "f3a877458c1045b181c310241afd7a6b"

console = Console()


def _parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="WebSocket Chat CLI for Assistant Interaction"
    )
    parser.add_argument("session_id", help="Session ID to use for the chat")
    parser.add_argument(
        "--ws-url",
        default=WS_BASE_URL,
        help=f"WebSocket base URL (default: {WS_BASE_URL})",
    )
    parser.add_argument("--api-key", default=API_KEY, help="API key for authentication")
    return parser.parse_args()


class WebSocketChatClient:
    """WebSocket chat client for interacting with assistants."""

    def __init__(self, ws_url: str, api_key: str, session_id: str):
        """
        Initialize the WebSocket chat client.

        Parameters
        ----------
        ws_url : str
            The WebSocket base URL
        api_key : str
            API key for authentication
        session_id : str
            Session ID for the chat
        """
        self.ws_url = f"{ws_url}/ws/main?api_key={api_key}"
        self.session_id = session_id
        self.websocket = None
        self.running = True
        self.current_message = ""
        self.live_display = None

    async def connect(self):
        """Connect to the WebSocket."""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            rprint("[green]✓ Connected to WebSocket[/green]")
            rprint(f"[blue]Session ID: {self.session_id}[/blue]")
            rprint(
                "[yellow]Type your messages and press Enter. Type 'quit' or 'exit' to leave.[/yellow]\n"
            )
        except Exception as e:
            rprint(f"[red]Failed to connect: {e}[/red]")
            raise

    async def send_message(self, content: str):
        """
        Send a message to the assistant.

        Parameters
        ----------
        content : str
            The message content to send
        """
        if not self.websocket:
            rprint("[red]Not connected to WebSocket[/red]")
            return

        message = {
            "event": "ingest_message",
            "data": {"content": content, "session_id": self.session_id},
        }

        try:
            await self.websocket.send(json.dumps(message))
            rprint(f"[dim]Sent: {content}[/dim]")
        except Exception as e:
            rprint(f"[red]Failed to send message: {e}[/red]")

    def _format_message_response(self, message_data: Dict[str, Any]) -> Panel:
        """Format a message response for display."""
        text = message_data.get("text", "")
        role = message_data.get("role", "assistant")
        annotations = message_data.get("annotations", [])

        content = Text(text)
        if annotations:
            content.append(f"\n\nAnnotations: {len(annotations)} items")

        return Panel(content, title=f"{role.title()}", border_style="green")

    def _format_tool_call(self, tool_data: Dict[str, Any]) -> Panel:
        """Format a tool call for display."""
        name = tool_data.get("name", "Unknown Tool")
        tool_id = tool_data.get("id", "")

        if name == "computer_tool":
            action = tool_data.get("action", {})
            status = tool_data.get("status", "")
            content = f"Action: {action}\nStatus: {status}"
        elif name == "file_search":
            queries = tool_data.get("queries", [])
            results = tool_data.get("results", [])
            content = f"Queries: {queries}\nResults: {len(results)} items"
        else:
            arguments = tool_data.get("arguments", "")
            content = f"Arguments: {arguments}"

        return Panel(
            content,
            title=f"[yellow]🔧 Tool Call: {name}[/yellow]",
            border_style="yellow",
        )

    def _format_tool_output(self, tool_data: Dict[str, Any]) -> Panel:
        """Format tool output for display."""
        output = tool_data.get("output", "")
        raw_output = tool_data.get("raw_output", "")

        display_output = output if output else raw_output
        if isinstance(display_output, dict):
            display_output = JSON.from_data(display_output)
        else:
            display_output = str(display_output)

        return Panel(
            display_output,
            title="[cyan]🔧 Tool Output[/cyan]",
            border_style="cyan",
        )

    def _format_agent_switch(self, agent_name: str) -> Panel:
        """Format agent switch notification."""
        return Panel(
            f"Switched to agent: {agent_name}",
            title="[magenta]🤖 Agent Switch[/magenta]",
            border_style="magenta",
        )

    def _format_handoff(self, action: str, from_agent: str, to_agent: str) -> Panel:
        """Format handoff notification."""
        content = f"Action: {action}\nFrom: {from_agent}\nTo: {to_agent}"
        return Panel(content, title="[blue]🔄 Handoff[/blue]", border_style="blue")

    async def handle_message(self, message: str):
        """
        Handle incoming WebSocket messages.

        Parameters
        ----------
        message : str
            The raw WebSocket message
        """
        try:
            data = json.loads(message)
            event_type = data.get("event")
            payload = data.get("data", {})

            if event_type != "agent_response":
                return

            kind = payload.get("kind")

            if kind == "token":
                # Handle streaming tokens
                delta = payload.get("delta", "")
                self.current_message += delta
                # Update live display if active
                if self.live_display:
                    self.live_display.update(
                        Panel(
                            self.current_message,
                            title="[green]Assistant (streaming...)[/green]",
                            border_style="green",
                        )
                    )

            elif kind == "message":
                # Complete message received
                if self.live_display:
                    # Update the live display with the final message before stopping
                    message_data = payload.get("message", {})
                    final_panel = self._format_message_response(message_data)
                    self.live_display.update(final_panel)

                    # Stop the live display after a brief moment to show the final state
                    await asyncio.sleep(0.1)
                    self.live_display.stop()
                    self.live_display = None
                else:
                    # If no live display was active, just print the message
                    message_data = payload.get("message", {})
                    panel = self._format_message_response(message_data)
                    console.print(panel)

                self.current_message = ""

            elif kind == "tool_call":
                tool_data = payload.get("tool", {})
                panel = self._format_tool_call(tool_data)
                console.print(panel)

            elif kind == "tool_output":
                tool_data = payload.get("tool", {})
                panel = self._format_tool_output(tool_data)
                console.print(panel)

            elif kind == "agent_switch":
                agent_name = payload.get("agent", "")
                panel = self._format_agent_switch(agent_name)
                console.print(panel)

            elif kind == "handoff":
                action = payload.get("action", "")
                from_agent = payload.get("from", "")
                to_agent = payload.get("to", "")
                panel = self._format_handoff(action, from_agent, to_agent)
                console.print(panel)

            elif kind == "done":
                rprint("[dim]--- Response Complete ---[/dim]\n")

        except json.JSONDecodeError:
            rprint(f"[red]Failed to parse message: {message}[/red]")
        except Exception as e:
            rprint(f"[red]Error handling message: {e}[/red]")

    async def listen_for_messages(self):
        """Listen for incoming WebSocket messages."""
        try:
            async for message in self.websocket:
                await self.handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            rprint("[yellow]WebSocket connection closed[/yellow]")
        except Exception as e:
            rprint(f"[red]Error listening for messages: {e}[/red]")

    async def run_chat(self):
        """Run the interactive chat loop."""
        await self.connect()

        # Start listening for messages in the background
        listen_task = asyncio.create_task(self.listen_for_messages())

        try:
            while self.running:
                try:
                    # Get user input
                    user_input = await asyncio.get_event_loop().run_in_executor(
                        None, input, "You: "
                    )

                    if user_input.lower() in ["quit", "exit"]:
                        break

                    if user_input.strip():
                        # Start live display for streaming response
                        self.live_display = Live(
                            Panel(
                                "",
                                title="[green]Assistant (waiting...)[/green]",
                            ),
                            console=console,
                            auto_refresh=True,
                            refresh_per_second=10,
                        )
                        self.live_display.start()

                        await self.send_message(user_input)

                except KeyboardInterrupt:
                    break
                except EOFError:
                    break

        finally:
            self.running = False
            if self.live_display:
                self.live_display.stop()
            listen_task.cancel()
            if self.websocket:
                await self.websocket.close()

    async def close(self):
        """Close the WebSocket connection."""
        if self.websocket:
            await self.websocket.close()


async def main():
    """Main entry-point for the WebSocket chat CLI."""
    args = _parse_args()

    client = WebSocketChatClient(
        ws_url=args.ws_url, api_key=args.api_key, session_id=args.session_id
    )

    # Handle graceful shutdown
    def signal_handler(signum, frame):
        client.running = False
        rprint("\n[yellow]Shutting down...[/yellow]")

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await client.run_chat()
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        sys.exit(1)
    finally:
        await client.close()
        rprint("[green]Goodbye![/green]")


if __name__ == "__main__":
    asyncio.run(main())

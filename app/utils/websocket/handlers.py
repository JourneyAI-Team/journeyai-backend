"""
WebSocket event handlers.

This module contains all the handlers for different WebSocket events.
Event handlers are responsible for processing WebSocket messages and
potentially spawning background tasks.
"""

import json
from typing import Any, Callable, List, Optional

from fastapi import WebSocket
from loguru import logger

# Registry to store all event handlers
event_handlers: dict[str, Callable] = {}


def register_handler(event_name: str) -> Callable:
    """
    Decorator to register a function as an event handler.

    Parameters
    ----------
    event_name : str
        The name of the event to handle.

    Returns
    -------
    Callable
        Decorator function.
    """

    def decorator(func: Callable) -> Callable:
        event_handlers[event_name] = func
        return func

    return decorator


# WebSocket connection store
# Maps connection_id to WebSocket instance
active_connections: dict[str, WebSocket] = {}


async def handle_event(
    connection_id: str, event_name: str, data: dict[str, Any]
) -> None:
    """
    Handle an incoming WebSocket event.

    Parameters
    ----------
    connection_id : str
        The ID of the WebSocket connection.
    event_name : str
        The name of the event to handle.
    data : dict[str, Any]
        The data associated with the event.
    """
    logger.info(f"Handling event: {event_name} for connection: {connection_id}")

    handler = event_handlers.get(event_name)
    if handler:
        try:
            await handler(connection_id, data)
        except Exception as e:
            logger.exception(f"Error handling event {event_name}: {str(e)}")
            await send_error(connection_id, f"Error processing event: {str(e)}")
    else:
        logger.warning(f"No handler found for event: {event_name}")
        await send_error(connection_id, f"Unknown event: {event_name}")


async def send_message(connection_id: str, event: str, data: dict[str, Any]) -> None:
    """
    Send a message to a specific WebSocket connection.

    Parameters
    ----------
    connection_id : str
        The ID of the WebSocket connection.
    event : str
        The name of the event.
    data : dict[str, Any]
        The data to send.
    """
    if connection_id in active_connections:
        websocket = active_connections[connection_id]
        message = {"event": event, "data": data}
        await websocket.send_text(json.dumps(message))
    else:
        logger.warning(
            f"Attempted to send message to non-existent connection: {connection_id}"
        )


async def send_error(connection_id: str, error_message: str) -> None:
    """
    Send an error message to a specific WebSocket connection.

    Parameters
    ----------
    connection_id : str
        The ID of the WebSocket connection.
    error_message : str
        The error message to send.
    """
    await send_message(connection_id, "error", {"message": error_message})


async def broadcast(
    event: str, data: dict[str, Any], exclude: Optional[List[str]] = None
) -> None:
    """
    Broadcast a message to all active WebSocket connections.

    Parameters
    ----------
    event : str
        The name of the event.
    data : dict[str, Any]
        The data to send.
    exclude : Optional[List[str]]
        List of connection IDs to exclude from the broadcast.
    """
    exclude = exclude or []
    for conn_id, websocket in active_connections.items():
        if conn_id not in exclude:
            message = {"event": event, "data": data}
            await websocket.send_text(json.dumps(message))

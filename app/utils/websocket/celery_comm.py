"""
Celery to WebSocket communication utilities.

This module provides utilities for Celery tasks to communicate with
WebSocket connections, even though they are in different processes.
"""

import json
from typing import Any, Dict

from loguru import logger

from app.clients.redis_client import get_redis_client


async def send_to_websocket(
    connection_id: str, event: str, data: Dict[str, Any]
) -> bool:
    """
    Send a message to a WebSocket connection from a Celery task.

    This function uses Redis pub/sub to communicate between the Celery task
    and the WebSocket server process.

    Parameters
    ----------
    connection_id : str
        The ID of the WebSocket connection.
    event : str
        The name of the event.
    data : Dict[str, Any]
        The data to send.

    Returns
    -------
    bool
        True if the message was published successfully, False otherwise.
    """
    try:
        message = {"connection_id": connection_id, "event": event, "data": data}

        # Get the redis client and publish the message
        redis_client = get_redis_client()
        redis_client.publish("websocket_messages", json.dumps(message))

        return True
    except Exception as e:
        logger.exception(f"Error sending message to WebSocket: {str(e)}")
        return False


async def send_to_all_websockets(event: str, data: Dict[str, Any]) -> bool:
    """
    Broadcast a message to all active WebSocket connections from a Celery task.

    Parameters
    ----------
    event : str
        The name of the event.
    data : Dict[str, Any]
        The data to send.

    Returns
    -------
    bool
        True if the message was published successfully, False otherwise.
    """
    try:
        message = {"broadcast": True, "event": event, "data": data}

        # Get the redis client and publish the message
        redis_client = get_redis_client()
        redis_client.publish("websocket_messages", json.dumps(message))

        return True
    except Exception as e:
        logger.exception(f"Error broadcasting message to WebSockets: {str(e)}")
        return False

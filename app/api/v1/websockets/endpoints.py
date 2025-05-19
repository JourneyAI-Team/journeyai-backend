"""
WebSocket endpoints for real-time communication.

This module provides WebSocket endpoints for real-time communication
between clients and the server, including streaming AI responses.
"""

import json
import uuid

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from loguru import logger

from app.api.deps import get_current_user
from app.models.user import User
from app.utils.websocket.handlers import (
    active_connections,
    handle_event,
    send_error,
    send_message,
)

router = APIRouter()


@router.websocket("/main")
async def authenticated_websocket_endpoint(
    websocket: WebSocket,
    current_user: User = Depends(get_current_user),
):
    """
    Authenticated WebSocket endpoint.

    This endpoint requires user authentication before establishing the WebSocket connection.
    """
    connection_id = str(uuid.uuid4())
    user_id = str(current_user.id)

    await websocket.accept()
    logger.info(
        f"Authenticated WebSocket connection established: {connection_id} for user: {user_id}"
    )

    # Store the connection
    active_connections[connection_id] = websocket

    try:
        # Send connection acknowledgment
        await send_message(
            connection_id,
            "connection_established",
            {"connection_id": connection_id, "user_id": user_id, "status": "connected"},
        )

        # Listen for messages
        while True:
            # Wait for a message from the client
            data = await websocket.receive_text()

            try:
                # Parse the JSON message
                message = json.loads(data)

                # Extract event and data
                event_name = message.get("event")
                event_data = message.get("data", {})

                # Add user information to the event data
                event_data["user_id"] = user_id

                if not event_name:
                    await send_error(connection_id, "Missing 'event' field in message")
                    continue

                # Handle the event
                await handle_event(connection_id, event_name, event_data)

            except json.JSONDecodeError:
                logger.warning(f"Received invalid JSON from client: {data}")
                await send_error(connection_id, "Invalid JSON message")
            except Exception as e:
                logger.exception(f"Error processing message: {str(e)}")
                await send_error(connection_id, f"Error processing message: {str(e)}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.exception(f"WebSocket error: {str(e)}")
    finally:
        # Clean up the connection
        if connection_id in active_connections:
            del active_connections[connection_id]
        logger.info(f"WebSocket connection removed: {connection_id}")

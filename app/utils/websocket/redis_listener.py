"""
Redis message listener for WebSockets.

This module listens for messages from Redis and relays them to the appropriate
WebSocket connections. This allows arq tasks to communicate with WebSockets
despite being in separate processes.
"""

import asyncio
import json
from typing import Any, Dict

from loguru import logger

from app.clients.redis_client import get_redis_async_client
from app.utils.websocket.handlers import active_connections, broadcast, send_message


class RedisListener:
    """
    Redis listener for WebSocket messages.

    Listens for messages published by arq tasks and relays them to
    the appropriate WebSocket connections.
    """

    def __init__(self):
        """Initialize the Redis listener."""
        self.redis_client = None
        self.pubsub = None
        self.running = False

    async def connect(self):
        """
        Connect to Redis and subscribe to the WebSocket messages channel.
        """
        self.redis_client = await get_redis_async_client()

        self.pubsub = self.redis_client.pubsub()
        await self.pubsub.subscribe("websocket_messages")
        logger.info(
            "Redis listener connected and subscribed to websocket_messages channel"
        )

    async def listen(self):
        """
        Start listening for messages from Redis.
        """
        if not self.pubsub:
            await self.connect()

        self.running = True

        while self.running:
            try:
                message = await self.pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=0.1
                )
                if message:
                    await self.process_message(message)

                # Reduced sleep to increase message fetch rate
                await asyncio.sleep(0.001)

            except Exception as e:
                logger.exception(f"Error processing Redis message: {str(e)}")
                # Add a delay before retrying
                await asyncio.sleep(1)

    async def process_message(self, message: Dict[str, Any]):
        """
        Process a message from Redis and relay it to the appropriate WebSocket.

        Parameters
        ----------
        message : Dict[str, Any]
            The message from Redis.
        """
        try:
            if message["type"] != "message":
                return

            data = json.loads(message["data"])

            # Check if it's a broadcast message
            if data.get("broadcast", False):
                event = data.get("event")
                event_data = data.get("data", {})
                await broadcast(event, event_data)
                logger.debug(f"Broadcast message sent: {event}")
            else:
                # It's a direct message to a specific connection
                connection_id = data.get("connection_id")
                event = data.get("event")
                event_data = data.get("data", {})

                if connection_id and connection_id in active_connections:
                    await send_message(connection_id, event, event_data)
                    logger.debug(f"Message sent to connection {connection_id}: {event}")
                else:
                    logger.warning(
                        f"Received message for non-existent connection: {connection_id}"
                    )

        except json.JSONDecodeError:
            logger.warning(f"Received invalid JSON from Redis: {message['data']}")
        except Exception as e:
            logger.exception(f"Error processing Redis message: {str(e)}")

    async def stop(self):
        """
        Stop listening for messages from Redis.
        """
        self.running = False
        if self.pubsub:
            await self.pubsub.unsubscribe()


# Global listener instance
listener = RedisListener()


async def start_redis_listener():
    """
    Start the Redis listener.

    This function should be called when the application starts.
    """
    logger.info("Starting Redis listener for WebSocket messages")
    asyncio.create_task(listener.listen())


async def stop_redis_listener():
    """
    Stop the Redis listener.

    This function should be called when the application shuts down.
    """
    logger.info("Stopping Redis listener for WebSocket messages")
    await listener.stop()

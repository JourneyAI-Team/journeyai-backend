import asyncio
import json
import sys

import httpx
from loguru import logger


class AsyncLokiSink:
    def __init__(self, loki_url, labels=None):
        self.loki_url = loki_url.rstrip("/")
        self.labels = labels or {"job": "journey"}
        self.queue = asyncio.Queue()
        self.client = httpx.AsyncClient()

        asyncio.create_task(self._worker())

    async def _worker(self):
        while True:
            log_record = await self.queue.get()
            await self._send_to_loki(log_record)
            self.queue.task_done()

    async def _send_to_loki(self, log_data):
        payload = {
            "streams": [
                {
                    "stream": self.labels,
                    "values": [
                        [
                            str(int(log_data["time"].timestamp() * 1e9)),
                            json.dumps(log_data),
                        ]
                    ],
                }
            ]
        }
        try:
            response = await self.client.post(
                f"{self.loki_url}/loki/api/v1/push",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            if response.status_code != 204:
                print(f"Loki push failed: {response.status_code} {response.text}")
        except Exception as e:
            print(f"Error sending to Loki: {e}")

    def write(self, message):
        try:
            log_record = json.loads(message)
            asyncio.create_task(self.queue.put(log_record))
        except Exception as e:
            print(f"Failed to enqueue log: {e}")

    def flush(self):
        pass


def setup_logger(loki_url: str, labels: dict = None):
    def serialize(record):
        return json.dumps(
            {
                "time": record["time"].isoformat(),
                "level": record["level"].name,
                "message": record["message"],
                "module": record["module"],
                "function": record["function"],
                "line": record["line"],
            }
        )

    logger.remove()
    logger.add(sys.stdout, serialize=serialize)

    loki_sink = AsyncLokiSink(loki_url, labels)
    logger.add(loki_sink, serialize=serialize)

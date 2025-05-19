from __future__ import annotations

import asyncio
import datetime as dt
import json
import sys
import time
from typing import Any, Dict, Optional

import httpx
from loguru import logger


class AsyncLokiSink:
    """
    Non-blocking sink that ships Loguru records to Grafana-Loki.

    Parameters
    ----------
    loki_url :
        Base URL where Loki is reachable, *e.g.* ``http://loki:3100``.
    labels :
        Default Loki stream labels. The key `job` is always recommended.
    queue_size :
        Maximum number of log records that may be queued before back-pressure.
    """

    def __init__(
        self,
        loki_url: str,
        labels: Optional[Dict[str, str]] = None,
        queue_size: int = 10_000,
    ) -> None:
        self._loki_url = loki_url.rstrip("/")
        self._labels = labels or {"job": "journey"}
        self._queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=queue_size)
        self._client = httpx.AsyncClient()
        asyncio.create_task(self._worker(), name="loki-worker")

    async def _worker(self) -> None:
        """Background task pulling logs from the queue and pushing to Loki."""
        while True:
            item = await self._queue.get()
            try:
                await self._send_to_loki(item)
            finally:
                self._queue.task_done()

    async def _send_to_loki(self, log: Dict[str, Any]) -> None:
        """Push a single log record to Loki."""
        payload = {
            "streams": [
                {
                    "stream": self._labels,
                    "values": [[log["ts_ns"], json.dumps(log)]],
                }
            ]
        }
        try:
            resp = await self._client.post(
                f"{self._loki_url}/loki/api/v1/push",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            if resp.status_code != 204:
                sys.stderr.write(
                    f"[Loki] push failed {resp.status_code}: {resp.text}\n"
                )
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"[Loki] error: {exc}\n")

    def write(self, message: str) -> None:  # noqa: D401
        """
        Conforms to Loguru's sink contract.

        Notes
        -----
        * ``logger.add(sink, serialize=...)`` sends each record as a JSON string.
        * We enrich the record with `ts_ns` so no further parsing is required.
        """
        if not message.strip():
            return  # Skip blank heartbeat lines produced by Loguru.
        try:
            log_dict: Dict[str, Any] = json.loads(message)

            # `time` comes in ISO-8601 form – turn it into nanoseconds once.
            if isinstance(log_dict["time"], str):
                timestamp = dt.datetime.fromisoformat(log_dict["time"])
                log_dict["ts_ns"] = str(int(timestamp.timestamp() * 1e9))
            else:  # pragma: no cover
                # Should never happen, but fallback to wall-clock.
                log_dict["ts_ns"] = str(int(time.time() * 1e9))

            asyncio.create_task(self._queue.put(log_dict))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"[Loki] enqueue failed: {exc}\n")

    def flush(self) -> None:  # noqa: D401
        """Required by file-like interface; nothing to flush (async)."""
        return None


def setup_logger(loki_url: str, labels: Optional[Dict[str, str]] = None) -> None:
    """
    Configure Loguru so ``from loguru import logger`` is production-ready.

    Parameters
    ----------
    loki_url :
        Endpoint of the Loki cluster.
    labels :
        Default Loki labels (merged with the sink-level defaults).
    """

    def _serializer(record: Dict[str, Any]) -> str:
        """
        Convert Loguru record → JSON string.

        Extra keys bound through ``logger.bind(...)`` are nested under
        ``record["extra"]``. They are flattened one level to maximise
        query flexibility in Loki.
        """
        base = {
            "time": record["time"].isoformat(),
            "level": record["level"].name,
            "message": record["message"],
            "module": record["module"],
            "function": record["function"],
            "line": record["line"],
        }
        # Flatten contextual data.
        if record["extra"]:
            base.update(record["extra"])
        return json.dumps(base)

    logger.remove()  # Drop default stderr sink
    logger.add(sys.stdout, serialize=_serializer, colorize=True)

    loki_sink = AsyncLokiSink(loki_url=loki_url, labels=labels)
    logger.add(loki_sink, serialize=_serializer)

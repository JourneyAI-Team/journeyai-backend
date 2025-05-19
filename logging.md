# Logging Standard

This project uses **Loguru** for application logging and pushes all records to **Grafana-Loki** for long-term storage and querying.

## 1. Quick-start

```python
from loguru import logger
from app.utils.loki_logger import setup_logger
setup_logger("http://loki:3100") # call once, e.g. in main.py
logger.info("App started")
```

## Contextual Logging

The `logger.contextualize()` method in Loguru is used to add context to log messages. This is particularly useful when you want to include additional information in your logs that can help with debugging or tracing the flow of execution.

When you use `logger.contextualize()`, it creates a context that is applied to all log messages within its scope. This means that any log message generated inside the `with` block will automatically include the context information specified. The context can include any key-value pairs that you want to attach to the logs.

### Example
When viewed in Grafana-Loki, any logs inside the context scope will have the `user_id` label.

```python
amount = 10 # Some arbitrary value
with logger.contextualize(user_id="u-123"):
    logger.debug("Will only appear when DEBUG is enabled")
    logger.info(f"Payment succeeded. {amount=}") # Outputs as "Payment succeeded. amount=10"
```


## 2. Severity levels

| Level | When to use | Examples |
|-------|-------------|----------|
| `trace`  | Very chatty, algorithm steps, loops | Deep protocol debugging |
| `debug`  | Anything useful when diagnosing a bug | Input/outputs of a function |
| `info`   | Normal, expected state transitions | User logged-in, job queued |
| `warning`| Anomalies that *might* become errors | Circuit-breaker half-open |
| `error`  | The operation failed but the app keeps running | Failed DB insert |
| `critical`| The process is compromised | Out-of-memory, data corruption |

*Golden rule*: **Log at the level that will matter tomorrow, not the level that feels safe today.**

## 3. Where to log

1. **Domain events** – user actions, workflow milestones  
2. **External I/O** – calls to databases, HTTP APIs, message queues  
3. **Error handling** – inside `except` blocks re-raising or swallowing exceptions  
4. **Startup / shutdown** – configuration, version, feature-flags  

## 4. Where *not* to log

* Hot inner-loops – use `trace` only when specifically debugging  
* Secrets or PII – never log passwords, tokens, card numbers  
* Large payloads – prefer a checksum or the first *n* bytes  

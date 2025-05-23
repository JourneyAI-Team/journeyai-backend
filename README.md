# Journey

Welcome to the Journey AI Repository!

---

## Prerequisites
* Python 3.10+
* [Poetry](https://python-poetry.org/docs/#installation)

---

## Installation

```bash
poetry install
```

---

## Environment variables

The application expects a `.env` file in the project root.

1. Open the **Journey** vault in 1Password.  
2. Copy the note that contains the `.env` contents.  
3. Create a file named `.env` in the project root and paste the copied text.

---

## Running the application locally

```bash
poetry run python -m app.main
```

---

## Running the RQ Workers

To process tasks in the background, you need to run RQ workers. Use the following command to start the workers for the queues:

```bash
rq worker artifacts_queue --url <redis_url>
```

Replace `<redis_url>` with the actual URL of your Redis server. You can specify multiple queues in order of priority if needed:

```bash
rq worker <queue_name1> <queue_name2> ... --url <redis_url>
```

### Why Multiple Queues?

Multiple queues allow you to prioritize tasks. For example, you might have a `high_priority_queue` for urgent tasks and a `low_priority_queue` for less critical tasks. By specifying multiple queues in order of priority, you ensure that more important tasks are processed first.

### Example

If you start 5 workers, each worker can be configured to accept tasks from specific queues only, or handle multiple queues. The priority of tasks is determined by the order of queues you pass to the worker. For instance:

```bash
rq worker high_priority_queue low_priority_queue --url <redis_url>
```

In this example, a single worker will process tasks from `high_priority_queue` first, and then from `low_priority_queue` once the high-priority tasks are completed. This setup allows you to efficiently manage resources and ensure critical tasks are prioritized.

Ensure that the Redis server is running and accessible at the specified URL.

---

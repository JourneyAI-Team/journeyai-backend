app: poetry run python -m app.main
artifacts_worker: arq app.workers.artifacts.worker.WorkerSettings
agents_worker: arq app.workers.agents.worker.WorkerSettings
messages_worker: arq app.workers.messages.worker.WorkerSettings
sessions_worker: arq app.workers.sessions.worker.WorkerSettings

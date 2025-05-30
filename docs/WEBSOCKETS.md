# WebSocket Event Documentation

This document outlines the various event types and data formats used for WebSocket communication in the application.

## Event Types and Data Formats

### 1. Connection Events

- **Event Name:** `connection_established`
- **Data Format:**
  ```json
  {
    "connection_id": "<str>",
    "user_id": "<str>",
    "status": "connected"
  }
  ```

### 2. Error Events

- **Event Name:** `error`
- **Data Format:**
  ```json
  {
    "message": "<str>"
  }
  ```

### 3. Agent Response Events

- **Event Name:** `agent_response`
- **Data Formats:**
  - **Token-level Streaming:**
    ```json
    {
      "kind": "token",
      "delta": "<str>",
      "ts": "<ISO 8601 timestamp>"
    }
    ```
  - **Agent Switch Notifications:**
    ```json
    {
      "kind": "agent_switch",
      "agent": "<str>",
      "ts": "<ISO 8601 timestamp>"
    }
    ```
  - **Message Output Created:**
    ```json
    {
      "kind": "message",
      "message": {
        "text": "<str>",
        "role": "<str>",
        "id": "<str>"
      },
      "ts": "<ISO 8601 timestamp>"
    }
    ```
  - **Tool Called:**
    ```json
    {
      "kind": "tool_call",
      "tool": {
        "id": "<str>",
        "name": "<str>",
        "arguments": "<str>"
      },
      "ts": "<ISO 8601 timestamp>"
    }
    ```
  - **Tool Output:**
     ```json
    {
      "kind": "tool_output",
      "tool": {
        "id": "<str>",
        "call_id": "<str>",
        "raw_output": "<str>",
        "output": "<str>"
      },
      "ts": "<ISO 8601 timestamp>"
    }
  - **Handoff Requested:**
    ```json
    {
      "kind": "handoff",
      "action": "requested",
      "from": "<str>",
      "to": "<str>",
      "ts": "<ISO 8601 timestamp>"
    }
    ```
  - **Handoff Occurred:**
    ```json
    {
      "kind": "handoff",
      "action": "completed",
      "from": "<str>",
      "to": "<str>",
      "ts": "<ISO 8601 timestamp>"
    }
    ```
  - **Done Marker:**
    ```json
    {
      "kind": "done",
      "session_id": "<str>",
      "ts": "<ISO 8601 timestamp>"
    }
    ```

### 4. Broadcast Events

- **Event Name:** `<dynamic_event_name>`
- **Data Format:**
  ```json
  {
    "event": "<str>",
    "data": "<dict>"
  }
  ```

### 5. Ingest Message Event

- **Event Name:** `ingest_message`
- **Data Format:**
  ```json
  {
    "content": "<str>",
    "attachments": ["<str>"],
    "assistant_id": "<str>",
    "account_id": "<str>",
    "session_id": "<str>"
  }
  ```

## Notes

- The `<str>` and `<dict>` placeholders indicate variable content that will be replaced with actual data during runtime.
- Timestamps are in ISO 8601 format to ensure consistency across different systems and time zones.
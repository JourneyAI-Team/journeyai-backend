# WebSocket API Documentation

This document provides a detailed guide on using the WebSocket API for real-time communication in the application. It includes information on how to connect, the types of events you can send and receive, and the data formats for each event type.

## Connecting to the WebSocket

To establish a WebSocket connection, use the following endpoint:

```
ws://<your-server-url>/ws/main
```

### Authentication

The WebSocket connection requires authentication. You must provide a valid API key obtained during the login process. The API key is used to authenticate the user and establish a secure connection.

## Base Message Format

All messages sent and received via the WebSocket follow a standard JSON format. The base structure is as follows:

```json
{
  "event": "<event_name>",
  "data": {
    // Event-specific data
  }
}
```

- **`event`**: A string representing the name of the event.
- **`data`**: A JSON object containing event-specific data.

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

These events are related to the agent's responses and actions.

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
    ```

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

## Example Usage

### Establishing a Connection

To establish a connection, use a WebSocket client to connect to the endpoint and authenticate using your API key.

### Sending a Message

To send a message, format your data according to the event type and send it through the WebSocket connection using the base message format.

### Receiving Messages

Listen for incoming messages on the WebSocket connection. The server will send messages in the formats described above.

## Notes

- The `<str>` and `<dict>` placeholders indicate variable content that will be replaced with actual data during runtime.
- Timestamps are in ISO 8601 format to ensure consistency across different systems and time zones.
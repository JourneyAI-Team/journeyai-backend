import datetime as dt
from pprint import pformat

from agents import ItemHelpers
from loguru import logger
from openai.types.responses.response_text_delta_event import ResponseTextDeltaEvent

from app.external.ai_service import generate_response
from app.utils.assistant_utils import get_agent_from_assistant
from app.utils.websocket.communications import send_to_websocket
from app.workers.agents.utils import (
    convert_messages_to_openai_format,
    fetch_message_history,
    get_objects_from_session,
)


async def process_session(ctx, connection_id: str, session_id: str):

    await send_to_websocket(
        connection_id, "processing_session", {"session_id": session_id}
    )

    # Get objects and perform checks
    session, assistant = await get_objects_from_session(session_id)

    # Fetch the last 100 messages from this session
    messages = await fetch_message_history(session_id)

    with logger.contextualize(
        session_id=session_id,
        assistant_id=assistant.id,
        user_id=session.user_id,
        organization_id=session.organization_id,
        message_id=messages[-1].id,
    ):

        agent = get_agent_from_assistant(assistant)
        logger.info(f"Agent: {agent}")
        logger.info(f"Fetched {len(messages)} messages in session: {session_id}")
        logger.debug(pformat(messages))
        logger.info(f"Processing session: {session_id}")

        # Convert the messages into a format OpenAI understands
        input = convert_messages_to_openai_format(messages)
        result = await generate_response(
            agent,
            input,
            session.user_id,
            session.organization_id,
            session.account_id,
            session_id,
        )

        async for event in result.stream_events():
            payload = {"ts": dt.datetime.now(tz=dt.timezone.utc).isoformat()}

            # ── 1. token-level streaming ──────────────────────────────────
            if event.type == "raw_response_event" and isinstance(
                event.data, ResponseTextDeltaEvent
            ):
                payload.update({"kind": "token", "delta": event.data.delta})
                await send_to_websocket(connection_id, "agent_response", payload)
                continue

            # ── 2. agent switch notifications ────────────────────────────
            if event.type == "agent_updated_stream_event":
                payload.update({"kind": "agent_switch", "agent": event.new_agent.name})
                await send_to_websocket(connection_id, "agent_response", payload)
                continue

            # ── 3. run-item events ───────────────────────────────────────
            if event.type != "run_item_stream_event":
                continue  # skip anything else

            it = event.item

            match event.name:
                case "message_output_created":
                    payload.update(
                        {
                            "kind": "message",
                            "message": {
                                "text": ItemHelpers.text_message_output(it),
                                "role": it.raw_item.role,
                                "id": getattr(it.raw_item, "id", None),
                            },
                        }
                    )

                case "tool_called":
                    tool_info = {
                        "id": getattr(it.raw_item, "id", None),
                        # Fallbacks cater for differences between LLM providers
                        "name": getattr(it.raw_item, "name", None)
                        or getattr(getattr(it.raw_item, "function", {}), "name", None),
                        "arguments": getattr(it.raw_item, "arguments", None)
                        or getattr(
                            getattr(it.raw_item, "function", {}), "arguments", None
                        ),
                    }
                    payload.update({"kind": "tool_call", "tool": tool_info})

                case "tool_output":
                    payload.update(
                        {
                            "kind": "tool_output",
                            "tool": {
                                "id": getattr(it.raw_item, "call_id", None),
                                "output": it.output,
                            },
                        }
                    )

                case "handoff_requested":
                    payload.update(
                        {
                            "kind": "handoff",
                            "action": "requested",
                            "from": getattr(it.agent, "name", None),
                            "to": getattr(
                                getattr(it.raw_item, "function", {}), "name", None
                            ),
                        }
                    )

                case "handoff_occured":
                    payload.update(
                        {
                            "kind": "handoff",
                            "action": "completed",
                            "from": getattr(it.source_agent, "name", None),
                            "to": getattr(it.target_agent, "name", None),
                        }
                    )

                case _:
                    continue  # ignore reasoning, MCP, etc.

            await send_to_websocket(connection_id, "agent_response", payload)

        # Final “done” marker (optional)
        await send_to_websocket(
            connection_id,
            "agent_response",
            {
                "kind": "done",
                "session_id": session_id,
                "ts": dt.datetime.now(tz=dt.timezone.utc).isoformat(),
            },
        )

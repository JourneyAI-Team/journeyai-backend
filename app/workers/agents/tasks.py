import datetime as dt
from pprint import pformat

from agents import ItemHelpers, RunResultStreaming
from agents.items import ResponseComputerToolCall, ResponseFunctionToolCall
from loguru import logger
from openai.types.responses.response_file_search_tool_call import (
    ResponseFileSearchToolCall,
)
from openai.types.responses.response_text_delta_event import ResponseTextDeltaEvent

from app.core.assistants import assistants_manager
from app.external.ai_service import generate_response
from app.models.message import Message
from app.schemas.types import SenderType
from app.utils.websocket.communications import send_to_websocket
from app.workers.agents.utils import (
    convert_messages_to_openai_format,
    fetch_message_history,
    get_objects_from_session,
)


async def emit_stream_events(
    connection_id: str, result: RunResultStreaming, session_id: str
):
    """
    Emit streaming events to the websocket.

    Parameters
    ----------
    connection_id : str
        The connection ID for the websocket.
    result : object
        The result object containing stream events.
    session_id : str
        The session ID for the current session.
    """
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

                annotations = []
                for content in it.raw_item.content:
                    if content.type == "output_text":
                        annotations.extend(
                            [a.model_dump() for a in content.annotations]
                        )

                payload.update(
                    {
                        "kind": "message",
                        "message": {
                            "text": ItemHelpers.text_message_output(it),
                            "role": it.raw_item.role,
                            "id": getattr(it.raw_item, "id", None),
                            "annotations": annotations,
                        },
                    }
                )

            case "tool_called":
                if isinstance(it.raw_item, ResponseFunctionToolCall):
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
                elif isinstance(it.raw_item, ResponseComputerToolCall):
                    tool_info = {
                        "id": it.raw_item.id,
                        "action": it.raw_item.action.model_dump(),
                        "name": "computer_tool",
                        "status": it.raw_item.status,
                        "pending_safety_checks": it.raw_item.pending_safety_checks,
                        "call_id": it.raw_item.call_id,
                    }
                elif isinstance(it.raw_item, ResponseFileSearchToolCall):
                    tool_info = {
                        "id": it.raw_item.id,
                        "queries": it.raw_item.queries,
                        "status": it.raw_item.status,
                        "name": it.raw_item.type,
                        "results": [r.model_dump() for r in it.raw_item.results or []],
                    }
                else:
                    tool_info = {
                        "id": it.raw_item.id,
                        "name": "web_search",
                        "status": it.raw_item.status,
                    }
                payload.update({"kind": "tool_call", "tool": tool_info})

            case "tool_output":

                if it.raw_item["type"] == "function_call_output":
                    tool_info = {
                        "id": it.raw_item.get("id"),
                        "call_id": it.raw_item["call_id"],
                        "raw_output": it.raw_item["output"],
                        "output": it.output,
                    }
                elif it.raw_item["type"] == "computer_call_output":
                    tool_info = {
                        "id": it.raw_item.get("id"),
                        "call_id": it.raw_item["call_id"],
                        "raw_output": it.raw_item["output"],
                        "output": it.output,
                    }
                else:
                    tool_info = {}

                payload.update(
                    {
                        "kind": "tool_output",
                        "tool": tool_info,
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


async def process_session(ctx, connection_id: str, session_id: str):
    """
    Process a session by fetching messages and generating a response.

    Parameters
    ----------
    ctx : object
        The context object.
    connection_id : str
        The connection ID for the websocket.
    session_id : str
        The session ID for the current session.
    """

    arq = ctx["arq"]

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

        agent = await assistants_manager.get_agent(assistant)
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
            assistant=assistant,
            history=messages,
        )

        # Stream events to the websocket for real time support
        await emit_stream_events(connection_id, result, session_id)

        # Save the response to the database
        new_items = [item.to_input_item() for item in result.new_items]
        for new_item in new_items:
            new_message = Message(
                output=new_item,
                sender=SenderType.ASSISTANT,
                user_id=session.user_id,
                organization_id=session.organization_id,
                session_id=session_id,
                account_id=session.account_id,
                assistant_id=assistant.id,
                embed_after_insert=True,
            )
            await new_message.save()

            await arq.enqueue_job(
                "post_message_creation",
                new_message.id,
                _queue_name="messages",
            )

import pprint

from agents import Agent, FileSearchTool, RunContextWrapper, WebSearchTool
from loguru import logger
from qdrant_client.models import FieldCondition, Filter, MatchValue

from app.core.config import settings
from app.external.ai_service import create_summary_for_search, get_embeddings
from app.models.assistant import Assistant
from app.models.user import User
from app.schemas.agent_context import AgentContext, InstructionsContext
from app.schemas.types import SenderType
from app.utils.prompt_utils import render_prompt_template
from app.utils.qdrant_utils import search_vectors
from app.utils.tool_utils import get_tool


class AssistantsManager:
    def __init__(self):
        pass

    async def get_agent(self, assistant: Assistant) -> Agent[AgentContext]:
        """
        Get an agent for an assistant.

        Parameters
        ----------
        assistant : Assistant
            The assistant to get an agent for.

        Returns
        -------
        Agent[AgentContext]
            The agent for the assistant.
        """

        # Create new agent if not in cache
        tools = self.get_tools(assistant)
        agent = Agent[AgentContext](
            name=assistant.name,
            model=assistant.model,
            tools=tools,
            instructions=self.create_instructions,
            reset_tool_choice=True,
        )

        return agent

    async def create_instructions(
        self, wrapper: RunContextWrapper[AgentContext], agent: Agent[AgentContext]
    ) -> str:
        """
        Create instructions for an assistant.

        Parameters
        ----------
        wrapper : RunContextWrapper[AgentContext]
            The wrapper for the agent context.
        agent : Agent[AgentContext]
            The agent to create instructions for.

        Returns
        -------
        str
            The instructions for the assistant.
        """

        with logger.contextualize(
            user_id=wrapper.context.user.id,
            organization_id=wrapper.context.organization.id,
            account_id=wrapper.context.account.id,
            session_id=wrapper.context.session.id,
            assistant_id=wrapper.context.assistant.id,
        ):

            logger.debug(f"Creating instructions for {wrapper.context.user}.")

            instructions_context = await self.generate_instructions_context(
                wrapper.context
            )
            logger.debug(
                f"Instructions context: {pprint.pformat(instructions_context)}"
            )

            instructions = render_prompt_template(
                "internal/context.md", {"instructions_context": instructions_context}
            )
            instructions = (
                f"{wrapper.context.assistant.developer_prompt}\n\n\n{instructions}"
            )
            logger.info(f"Created instructions for {wrapper.context.user}.")

            return instructions

    async def generate_instructions_context(
        self, context: AgentContext
    ) -> InstructionsContext:
        """
        Generate instructions context for an assistant.

        Parameters
        ----------
        context : AgentContext
            The context for the assistant.

        Returns
        -------
        InstructionsContext
            The instructions context for the assistant.
        """

        with logger.contextualize(
            user_id=context.user.id,
            organization_id=context.organization.id,
            account_id=context.account.id,
            session_id=context.session.id,
            assistant_id=context.assistant.id,
            message_id=context.history[-1].id,
        ):
            logger.debug(f"Generating instructions context for {context.user}.")

            search_query = await create_summary_for_search(context.history)
            logger.info(f"Search query: {search_query}")

            # Fetch related objects
            related_artifacts = await self._search_related_artifacts(
                search_query, context.account.id
            )
            related_messages = await self._search_related_messages(
                search_query, context.account.id, context.session.id
            )
            logger.debug(f"Related artifacts: {pprint.pformat(related_artifacts)}")
            logger.debug(f"Related messages: {pprint.pformat(related_messages)}")

            # Fetch user profile
            user_profile = self._parse_user_profile(context.user)
            logger.debug(f"User profile: {pprint.pformat(user_profile)}")

            return InstructionsContext(
                user_profile=user_profile,
                account_info=context.account.model_dump(),
                related_artifacts=related_artifacts,
                related_messages=related_messages,
            )

    def _parse_related_artifacts(self, artifacts: list[dict]) -> list[dict]:
        """
        Parse the related artifacts into a list of dictionaries.
        """
        related_artifacts = []
        for artifact in artifacts:
            related_artifacts.append(
                {
                    "id": artifact.id,
                    "title": artifact.payload["title"],
                    "body": artifact.payload["body"],
                    "type": artifact.payload["type"],
                }
            )
        return related_artifacts

    def _parse_related_messages(self, messages: list[dict]) -> list[dict]:
        """
        Parse the related messages into a list of dictionaries.
        """
        related_messages = []
        for message in messages:
            data = {
                "id": message.id,
                "sender": message.payload["sender"],
            }

            if data["sender"] == SenderType.USER.value:
                data["content"] = message.payload["input"]["content"]
            else:
                data["content"] = message.payload["output"]

                # Remove file search results to not waste tokens
                if data["content"].get("type") == "file_search_call":
                    data["content"].pop("results", None)

            related_messages.append(data)

        return related_messages

    def _parse_user_profile(self, user: User) -> dict:
        """
        Parse the user profile into a dictionary.
        """

        profile = user.profile
        profile_dict = (
            profile.model_dump() if hasattr(profile, "model_dump") else profile.__dict__
        )
        return {
            k: v
            for k, v in profile_dict.items()
            if v is not None and v != [] and v != {}
        }

    async def _search_related_artifacts(
        self, search_query: str, account_id: str
    ) -> list[dict]:
        """
        Search for related artifacts in the database.
        """
        related_artifacts = await search_vectors(
            collection_name="Artifacts",
            query_embedding=await get_embeddings(search_query),
            top_k=10,
            score_threshold=settings.RELATED_ARTIFACTS_SCORE_THRESHOLD,
            filter=Filter(
                must=[
                    FieldCondition(key="account_id", match=MatchValue(value=account_id))
                ],
                must_not=[
                    FieldCondition(
                        key="type",
                        match=MatchValue(value="assistant_document"),
                    ),
                ],
            ),
        )
        return self._parse_related_artifacts(related_artifacts)

    async def _search_related_messages(
        self, search_query: str, account_id: str, session_id: str
    ) -> list[dict]:
        """
        Search for related messages in the database.
        """
        related_messages = await search_vectors(
            collection_name="Messages",
            query_embedding=await get_embeddings(search_query),
            top_k=20,
            score_threshold=settings.RELATED_MESSAGES_SCORE_THRESHOLD,
            filter=Filter(
                must=[
                    FieldCondition(
                        key="account_id", match=MatchValue(value=account_id)
                    ),
                ],
                must_not=[
                    FieldCondition(key="session_id", match=MatchValue(value=session_id))
                ],
            ),
        )
        return self._parse_related_messages(related_messages)

    def get_tools(self, assistant: Assistant) -> list:
        """
        Get the tools for an assistant.

        Parameters
        ----------
        assistant : Assistant
            The assistant to get the tools for.

        Returns
        -------
        list
            A list of tools for the assistant.
        """

        tools = []

        for tool in assistant.tool_config["tools"]:
            match tool["name"]:
                case "openai_web_search":
                    tools.append(WebSearchTool())
                case _:
                    tools.append(get_tool(tool["name"], tool["type"]))

        if assistant.tool_config.get("vector_store_ids"):
            vector_store_ids = [i for i in assistant.tool_config["vector_store_ids"]]
            tools.append(
                FileSearchTool(
                    vector_store_ids=vector_store_ids, include_search_results=True
                )
            )

        return tools


assistants_manager = AssistantsManager()

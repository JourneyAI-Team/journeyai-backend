from typing import Callable

from agents import RunContextWrapper, function_tool

from app.clients.arq_client import get_arq
from app.models.artifact import Artifact
from app.schemas.agent_context import AgentContext
from app.schemas.types import OriginType


@function_tool
async def save_artifact(
    wrapper: RunContextWrapper[AgentContext], artifact_type: str, title: str, body: str
) -> dict:
    """**CRITICAL FOR MEMORY RETENTION** - Save important research findings and insights permanently.

    This is your ONLY way to preserve information across conversations and sessions. ALL research
    findings, insights, and important details will be lost when the chat ends unless you save them here.

    **WHEN TO USE THIS TOOL:**
    - After completing any research task or gathering significant information
    - When you discover key insights about a company, industry, or competitive landscape
    - When you identify important stakeholder information or contact details
    - After analyzing customer profiles, market positioning, or strategic insights
    - When preparing meeting summaries or action items
    - Whenever you want to reference specific findings in future conversations

    **RESEARCH-SPECIFIC USAGE:**
    - Save company profiles, competitive analyses, and industry insights
    - Store stakeholder research and key decision-maker information
    - Preserve customer profile findings and target market analysis
    - Record strategic recommendations and meeting preparation notes

    Use this tool proactively throughout your research process - not just at the end.
    Think of this as building a permanent knowledge base for ongoing client relationships.

    Args:
        artifact_type (str): The type of research artifact (e.g., "company_profile", "competitive_analysis",
            "stakeholder_research", "industry_insights", "customer_profile", "meeting_prep")
        title (str): Clear, descriptive title for easy future reference
        body (str): Detailed content including key findings, insights, and actionable information

    Returns:
        dict: Confirmation with the ID of the saved artifact
    """

    arq = await get_arq()

    new_artifact = Artifact(
        type=artifact_type,
        title=title,
        body=body,
        origin_type=OriginType.LLM,
        user_id=wrapper.context.user.id,
        organization_id=wrapper.context.organization.id,
        account_id=wrapper.context.account.id,
        session_id=wrapper.context.session.id,
    )
    await new_artifact.insert()
    await arq.enqueue_job(
        "post_artifact_creation", new_artifact.id, _queue_name="artifacts"
    )

    return {"id": new_artifact.id}


def get_tool() -> Callable:
    return save_artifact

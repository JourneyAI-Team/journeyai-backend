from beanie.operators import In
from fastapi import APIRouter, HTTPException, Query, status
from loguru import logger

from app.models.assistant import Assistant
from app.schemas.assistant import (
    AssistantCategoryRead,
    AssistantCreate,
    AssistantRead,
    AssistantUpdate,
)
from app.schemas.types import AssistantCategoryType

router = APIRouter()


@router.post(
    "/",
    response_model=AssistantRead,
    status_code=status.HTTP_201_CREATED,
    description="Create an assistant.",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Assistant with the same internal_name and version already exists."
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Error creating assistant."
        },
    },
)
async def create_assistant(assistant: AssistantCreate):
    logger.info(f"Create assistant request received. {assistant.name}")

    # Check if an assistant with the same internal_name and version already exists
    existing_assistant = await Assistant.find_one(
        Assistant.internal_name == assistant.internal_name,
        Assistant.version == assistant.version,
    )
    if existing_assistant:
        logger.warning(
            f"Assistant with internal_name '{assistant.internal_name}' and version '{assistant.version}' already exists."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assistant with the same internal_name and version already exists.",
        )

    new_assistant = Assistant(
        name=assistant.name,
        internal_name=assistant.internal_name,
        description=assistant.description,
        category=assistant.category,
        tool_config=assistant.tool_config,
        testing=assistant.testing,
        version=assistant.version,
        developer_prompt=assistant.developer_prompt,
        model=assistant.model,
    )

    try:
        await new_assistant.insert()
        logger.success(f"Assistant created successfully. {assistant.name}")
    except Exception as e:
        logger.exception(
            f"Database insert failed when creating assistant. {assistant.name}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating assistant.",
        ) from e

    return new_assistant


@router.get(
    "/",
    response_model=list[AssistantRead],
    status_code=status.HTTP_200_OK,
    description="List all assistants. Optionally filter by category.",
)
async def list_assistants(
    category: str | None = Query(None, description="Filter assistants by category"),
    ids: list[str] | None = Query(None, description="Filter assistants by ids"),
):
    logger.info(
        f"List assistants request received. Category filter: {category}; ids filter: {ids}"
    )

    if ids:
        assistants = await Assistant.find(In(Assistant.id, ids)).to_list()
        logger.info(f"Found {len(assistants)} assistants in ids '{ids}'.")
    elif category:
        assistants = await Assistant.find(
            Assistant.category == category.lower()
        ).to_list()
        logger.info(f"Found {len(assistants)} assistants in category '{category}'.")
    else:
        assistants = await Assistant.find_all().to_list()
        logger.info(f"Found {len(assistants)} assistants total.")

    return assistants


@router.get(
    "/categories",
    response_model=AssistantCategoryRead,
    status_code=status.HTTP_200_OK,
    description="List all assistant categories.",
)
async def list_assistant_categories():
    logger.info("List assistant categories request received.")

    return AssistantCategoryRead(assistant_categories=list(AssistantCategoryType))


@router.get(
    "/{assistant_id}",
    response_model=AssistantRead,
    status_code=status.HTTP_200_OK,
    description="Get an assistant by ID.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Assistant does not exist."},
    },
)
async def get_assistant(assistant_id: str):
    logger.info(f"Get assistant request received. {assistant_id}")

    assistant = await Assistant.find_one(Assistant.id == assistant_id)
    if not assistant:
        logger.warning(f"Assistant does not exist. {assistant_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assistant does not exist.",
        )

    return assistant


@router.patch(
    "/{assistant_id}",
    response_model=AssistantRead,
    status_code=status.HTTP_200_OK,
    description="Update an assistant.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Assistant does not exist."},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Error updating assistant."
        },
    },
)
async def update_assistant(assistant_id: str, assistant_in: AssistantUpdate):
    with logger.contextualize(assistant_id=assistant_id):
        logger.info(f"Update assistant request received. {assistant_id}")

        # Check if assistant exists
        assistant = await Assistant.find_one(Assistant.id == assistant_id)
        if not assistant:
            logger.warning(f"Assistant does not exist. {assistant_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assistant does not exist.",
            )

        try:
            # Update the assistant with only provided fields
            update_data = assistant_in.model_dump(exclude_unset=True)
            await assistant.set(update_data)
            logger.success(f"Assistant updated successfully. {assistant_id}")
        except Exception as e:
            logger.exception(
                f"Database update failed when updating assistant. {assistant_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating assistant.",
            ) from e

        return assistant


@router.delete(
    "/{assistant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete an assistant.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Assistant could not be found."},
    },
)
async def delete_assistant(assistant_id: str):
    with logger.contextualize(assistant_id=assistant_id):
        logger.info(f"Delete assistant request received. {assistant_id}")

        assistant = await Assistant.find_one(Assistant.id == assistant_id)
        if not assistant:
            logger.warning(f"Assistant could not be found. {assistant_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assistant could not be found.",
            )

        try:
            # Delete the assistant
            await assistant.delete()
            logger.success(f"Assistant deleted successfully. {assistant_id}")
        except Exception as e:
            logger.exception(
                f"Database delete failed when deleting assistant. {assistant_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting assistant.",
            ) from e

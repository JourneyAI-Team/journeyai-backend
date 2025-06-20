from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.profile import AssistantNotesUpdate, ProfileRead, ProfileUpdate

router = APIRouter()


@router.get(
    "/",
    response_model=ProfileRead,
    status_code=status.HTTP_200_OK,
    description="Retrieve the currently authenticated user's profile.",
)
async def get_profile(current_user: User = Depends(get_current_user)):
    with logger.contextualize(user_id=current_user.id):
        logger.info("Retrieve profile request received.")
        return current_user.profile


@router.patch(
    "/",
    response_model=ProfileRead,
    status_code=status.HTTP_200_OK,
    description="Update the currently authenticated user's profile with partial support.",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Error updating profile."
        }
    },
)
async def update_profile(
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_user),
):
    with logger.contextualize(user_id=current_user.id):
        logger.info(f"Update profile request received. {profile_update=}")

        try:
            # Get only the fields that were set (exclude unset fields for partial updates)
            update_data = profile_update.model_dump(exclude_unset=True)
            
            if update_data:
                # Update the profile fields
                profile_dict = current_user.profile.model_dump()
                
                # Remove possible duplicates from favorite assistants
                new_favorite_assistants = update_data.get("favorite_assistants")
                cur_favorite_assistants = profile_dict.get("favorite_assistants")
                
                if new_favorite_assistants and cur_favorite_assistants:
                    update_data["favorite_assistants"] = list(set(new_favorite_assistants + cur_favorite_assistants))
                elif new_favorite_assistants and not cur_favorite_assistants:
                    update_data["favorite_assistants"] = list(set(new_favorite_assistants))
                
                profile_dict.update(update_data)
                
                # Update the user's profile in the database
                await current_user.set({User.profile: profile_dict})

                # Refresh the user to get the updated profile
                await current_user.sync()

                logger.success("Profile updated successfully.")
            else:
                logger.info("No profile fields to update.")

        except Exception as e:
            logger.exception(
                f"Database update failed when updating profile for user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating profile.",
            ) from e

        return current_user.profile


@router.put(
    "/assistant-notes/{assistant_id}",
    response_model=ProfileRead,
    status_code=status.HTTP_200_OK,
    description="Add or update assistant notes for the user's profile.",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Error updating assistant notes."
        }
    },
)
async def update_assistant_notes(
    assistant_id: str,
    notes_update: AssistantNotesUpdate,
    current_user: User = Depends(get_current_user),
):
    with logger.contextualize(user_id=current_user.id, assistant_id=assistant_id):
        logger.info("Update assistant notes request received.")

        try:
            # Get current profile
            profile_dict = current_user.profile.model_dump()

            # Initialize assistant_notes if it doesn't exist
            if not profile_dict.get("assistant_notes"):
                profile_dict["assistant_notes"] = {}

            # Update the assistant notes
            profile_dict["assistant_notes"][assistant_id] = notes_update.notes

            # Update the user's profile in the database
            await current_user.set({User.profile: profile_dict})

            # Refresh the user to get the updated profile
            await current_user.sync()

            logger.success("Assistant notes updated successfully.")

        except Exception as e:
            logger.exception(
                f"Database update failed when updating assistant notes for user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating assistant notes.",
            ) from e

        return current_user.profile


@router.delete(
    "/assistant-notes/{assistant_id}",
    response_model=ProfileRead,
    status_code=status.HTTP_200_OK,
    description="Delete assistant notes for the user's profile.",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Error deleting assistant notes."
        }
    },
)
async def delete_assistant_notes(
    assistant_id: str,
    current_user: User = Depends(get_current_user),
):
    with logger.contextualize(user_id=current_user.id, assistant_id=assistant_id):
        logger.info("Delete assistant notes request received.")

        try:
            # Get current profile
            profile_dict = current_user.profile.model_dump()

            # Remove the assistant notes if they exist
            if (
                profile_dict.get("assistant_notes")
                and assistant_id in profile_dict["assistant_notes"]
            ):
                del profile_dict["assistant_notes"][assistant_id]

                # Update the user's profile in the database
                await current_user.set({User.profile: profile_dict})

                # Refresh the user to get the updated profile
                await current_user.sync()

                logger.success("Assistant notes deleted successfully.")
            else:
                logger.info("No assistant notes found to delete.")

        except Exception as e:
            logger.exception(
                f"Database update failed when deleting assistant notes for user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting assistant notes.",
            ) from e

        return current_user.profile

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.api.deps import get_current_user
from app.models.account import Account
from app.models.user import User
from app.schemas.account import AccountCreate, AccountRead, AccountUpdate

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=AccountRead,
    description="Create an account under an organization.",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Account with the same name already exists."
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Error creating account."
        },
    },
)
async def create_account(
    account: AccountCreate,
    current_user: User = Depends(get_current_user),
):
    with logger.contextualize(
        user_id=current_user.id,
        organization_id=current_user.organization_id,
    ):
        logger.info(f"Create account request received. {account.name=}")

        # Find if account exists in the current_user's organization
        existing_account = await Account.find_one(
            Account.organization_id == current_user.organization_id,
            Account.name == account.name,
        )
        if existing_account:
            logger.warning(
                f"Account already registered in the organization. {account.name=}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account already registered in the organization.",
            )

        # Create the new account
        new_account = Account(
            name=account.name,
            description=account.description,
            organization_id=current_user.organization_id,
            user_id=current_user.id,
        )

        try:
            # Save the new account to the database
            await new_account.insert()
            logger.success(f"Account created successfully. {account.name=}")
        except Exception as e:
            logger.exception(
                f"Database insert failed when creating account. {account.name=}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating account.",
            ) from e

        return new_account


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[AccountRead],
    description="List accounts in an organization.",
)
async def list_accounts(
    current_user: User = Depends(get_current_user),
):

    with logger.contextualize(
        user_id=current_user.id, organization_id=current_user.organization_id
    ):
        logger.info("List accounts request received.")

        accounts = await Account.find(
            Account.organization_id == current_user.organization_id
        ).to_list()

        logger.info(f"Found {len(accounts)} accounts in the organization.")

        return accounts


@router.get(
    "/{account_id}",
    status_code=status.HTTP_200_OK,
    response_model=AccountRead,
    description="Retrieve an account in an organization by its id.",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Account could not be found within the organization."
        },
    },
)
async def get_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
):
    with logger.contextualize(
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        account_id=account_id,
    ):
        logger.info("Retrieve account request received.")

        account = await Account.find_one(
            Account.organization_id == current_user.organization_id,
            Account.id == account_id,
        )
        if not account:
            logger.warning("Account could not be found within the organization.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account could not be found within the organization.",
            )

        logger.success("Account retrieved successfully.")
        return account


@router.patch(
    "/{account_id}",
    status_code=status.HTTP_200_OK,
    response_model=AccountRead,
    description="Update an account in an organization by its id.",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Account could not be found within the organization."
        },
    },
)
async def update_account(
    account_id: str,
    account_in: AccountUpdate,
    current_user: User = Depends(get_current_user),
):

    with logger.contextualize(
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        account_id=account_id,
    ):
        logger.info(f"Update account request received. {account_in=}")

        # Check if account exists in the organization the current user is in
        account = await Account.find_one(
            Account.organization_id == current_user.organization_id,
            Account.id == account_id,
        )
        if not account:
            logger.warning("Account could not be found within the organization.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account could not be found within the organization.",
            )

        await account.set(account_in)
        logger.success("Account updated successfully.")

    return account


@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete an account under an organization.",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Account could not be found within the organization."
        },
    },
)
async def delete_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
):

    with logger.contextualize(
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        account_id=account_id,
    ):
        logger.info("Delete account request received.")

        # Check if account exists in the organization the current user is in
        account = await Account.find_one(
            Account.organization_id == current_user.organization_id,
            Account.id == account_id,
        )
        if not account:
            logger.warning("Account could not be found within the organization.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account could not be found within the organization.",
            )

        # Delete the account
        await account.delete()
        logger.success("Account deleted successfully.")

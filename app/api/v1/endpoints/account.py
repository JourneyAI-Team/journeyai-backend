from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.account import Account
from app.models.user import User
from app.schemas.account import AccountCreate, AccountRead, AccountUpdate

router = APIRouter()


@router.post("/")
async def create_account(
    account: AccountCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Create an account under an organization.

    Parameters
    -----
    account: AccountCreate
        Request body. Fields required to create an account.

    Returns
    -----
    dict
        Empty dictionary

    Raises
    -----
    HTTPException
        400 if the account is already registered in the organization
    """

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
        except Exception as e:
            logger.exception(
                f"Database insert failed when creating account. {account.name=}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating account.",
            ) from e

        return new_account


@router.get("/", response_model=List[AccountRead])
async def list_accounts(
    current_user: User = Depends(get_current_user),
):
    """
    List accounts in an organization.

    Parameters
    -----

    Returns
    -----
    list(AccountRead)
        List of account object dictionaries.

    """
    accounts = await Account.find(
        Account.organization_id == current_user.organization_id
    ).to_list()
    return accounts


@router.get("/{account_id}", response_model=AccountRead)
async def get_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve an account in an organization by its id.

    Parameters
    -----

    Returns
    -----
    dict
        ``id`` - account id.
        ``name`` - account name.
        ``description`` - account description.
        ``organization_id`` - ID of the organization the account belongs to

    Raises
    -----
    HTTPException
        404 if account could not be found within an organization
    """

    account = await Account.find_one(
        Account.organization_id == current_user.organization_id,
        Account.id == account_id,
    )
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account could not be found within the organization.",
        )

    return account


@router.patch("/{account_id}")
async def update_account(
    account_id: str,
    account_in: AccountUpdate,
    current_user: User = Depends(get_current_user),
):
    """
    Update an account in an organization by its id.

    Parameters
    -----
    account_id: str
        Path parameter. The account id to update.
    account_in: AccountUpdate
        Request Body. Contains the description field.

    Returns
    -----
    dict
        Empty Dictionary

    Raises
    -----
    HTTPException
        404 if account could not be found within an organization
    """

    # Check if account exists in the organization the current user is in
    account = await Account.find_one(
        Account.organization_id == current_user.organization_id,
        Account.id == account_id,
    )
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account could not be found within the organization.",
        )

    # Update the account, only description is allowed to be updated
    await account.set({Account.description: account_in.description})

    return {}


@router.delete("/{account_id}")
async def delete_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Delete an account under an organization.

    Parameters
    -----
    account_id: str
        The id of the account to delete.

    Returns
    -----
    dict
        Empty Dictionary

    Raises
    -----
    HTTPException
        404 if account could not be found within an organization
    """

    # Check if account exists in the organization the current user is in
    account = await Account.find_one(
        Account.organization_id == current_user.organization_id,
        Account.id == account_id,
    )
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account could not be found within the organization.",
        )

    # Delete the account
    await account.delete()

    return {}

import argparse
import asyncio
from typing import List

from faker import Faker
from tqdm.asyncio import tqdm_asyncio  # nice progress bar for asyncio

from app.db.init_mongo import init_db
from app.models.account import Account
from app.models.organization import Organization
from app.models.session import Session
from app.models.user import User

fake = Faker()


def _parse_args() -> argparse.Namespace:  # noqa: D401
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Seed MongoDB with fake data")
    parser.add_argument("--orgs", type=int, default=50)
    parser.add_argument("--users-per-org", type=int, default=200)
    parser.add_argument("--accounts-per-org", type=int, default=300)
    parser.add_argument("--sessions-per-account", type=int, default=50)
    return parser.parse_args()


async def _build_organizations(n: int) -> List[Organization]:
    """Return ``n`` fake organizations."""
    return [
        Organization(name=fake.company(), domain=f"{fake.domain_name()}")
        for _ in range(n)
    ]


async def _build_users(orgs: List[Organization], n_per_org: int) -> List[User]:
    """Return a list of users for each organization."""
    users: list[User] = []
    for org in orgs:
        users.extend(
            [
                User(
                    email=fake.unique.email(),
                    hashed_password="not_relevant_for_benchmark",
                    organization_id=org.id,
                )
                for _ in range(n_per_org)
            ]
        )
    return users


async def _build_accounts(orgs: List[Organization], n_per_org: int) -> List[Account]:
    """Return a list of accounts for each organization."""
    accounts: list[Account] = []
    for org in orgs:
        accounts.extend(
            [
                Account(
                    name=fake.company(),
                    description=fake.catch_phrase(),
                    organization_id=org.id,
                    user_id=fake.uuid4(),
                )
                for _ in range(n_per_org)
            ]
        )
    return accounts


async def _build_sessions(accounts: List[Account], n_per_account: int) -> List[Session]:
    """Return a list of sessions for each account."""
    sessions: list[Session] = []
    for acc in accounts:
        sessions.extend(
            [
                Session(
                    title=fake.bs().title(),
                    summary=fake.sentence(),
                    account_id=acc.id,
                    assistant_id="benchmark_assistant",
                    user_id=fake.uuid4(),
                    organization_id=acc.organization_id,
                )
                for _ in range(n_per_account)
            ]
        )
    return sessions


async def seed_db() -> None:
    """
    Entry-point for seeding.

    The function orchestrates:

    1. Connecting to MongoDB via ``init_db``.
    2. Building fake documents.
    3. Bulk-inserting in batches to avoid huge RAM spikes.
    """
    args = _parse_args()
    await init_db()

    orgs = await _build_organizations(args.orgs)
    users = await _build_users(orgs, args.users_per_org)
    accounts = await _build_accounts(orgs, args.accounts_per_org)
    sessions = await _build_sessions(accounts, args.sessions_per_account)

    # Insert in a deterministic order (parents first)
    for model, docs in [
        (Organization, orgs),
        (User, users),
        (Account, accounts),
        (Session, sessions),
    ]:
        # tqdm_asyncio makes await-able iterations look nice in the console
        for chunk in tqdm_asyncio(
            [docs[i : i + 1_000] for i in range(0, len(docs), 1_000)],
            desc=f"Inserting {model.__name__}",
        ):
            await model.insert_many(chunk)


if __name__ == "__main__":
    asyncio.run(seed_db())

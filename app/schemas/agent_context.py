import dataclasses

from app.models.account import Account
from app.models.assistant import Assistant
from app.models.message import Message
from app.models.organization import Organization
from app.models.session import Session
from app.models.user import User


@dataclasses.dataclass
class AgentContext:
    user: User
    organization: Organization
    account: Account
    session: Session
    assistant: Assistant
    history: list[Message]

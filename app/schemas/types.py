from enum import Enum


class SenderType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class RoleType(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"

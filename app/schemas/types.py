from enum import Enum


class SenderType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class RoleType(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


class OriginType(str, Enum):
    LLM = "llm"
    USER = "User"


class ToolType(str, Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"


class EmbeddingInputSourceType(str, Enum):
    USER = "user"

class AssistantCategoryType(str, Enum):
    ACCOUNT_STRATEGY = "account strategy"
    PROSPECTING = "prospecting"
    RESEARCH = "research"
    CLOSING_SALES = "closing sales"
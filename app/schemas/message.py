from typing_extensions import TypedDict


class InputMessageSchema(TypedDict):
    content: str
    attachments: list[str]

    assistant_id: str
    session_id: str
    account_id: str

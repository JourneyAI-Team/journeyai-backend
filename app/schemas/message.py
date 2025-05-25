from typing_extensions import NotRequired, TypedDict


class IngestMessageSchema(TypedDict):
    content: str
    attachments: NotRequired[list[str]]

    assistant_id: str
    account_id: str
    session_id: str


class InputMessageSchema(TypedDict):
    content: str

from typing import Any
from pydantic.dataclasses import dataclass
from .data_type import Item

@dataclass
class Session:
    user_name: str
    user_id: str
    session_id: str


@dataclass
class Request:
    contents: list[Item]
    metadata: dict[str, Any]
    session: Session


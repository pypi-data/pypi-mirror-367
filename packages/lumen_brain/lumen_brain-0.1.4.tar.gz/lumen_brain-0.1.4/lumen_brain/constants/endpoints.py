"""
File: endpoints.py
Created Date: Tuesday July 22nd 2025
Author: Christian Nonis <alch.infoemail@gmail.com>
"""

from enum import Enum
from typing import Literal, Optional, Union
from pydantic import BaseModel, Field

API_VERSION = "v1"
BASE_URL = f"https://api.brainapi.lumen-labs.ai/api/{API_VERSION}"

MEMORY_CONTENT_TYPES = Literal[
    "file",
    "file_chunk",
    "event",
    "webpage",
    "webpage_chunk",
    "email",
    "email_chunk",
]
ALL_MEMORY_CONTENT_TYPES = Union[Literal["message"], MEMORY_CONTENT_TYPES]

API_KEY_HEADER = "X-LumenBrain-ApiKey"


class MemoryEndpoints(str, Enum):
    UPDATE = f"{BASE_URL}/memory/update"
    QUERY = f"{BASE_URL}/memory/query"
    TASKS = f"{BASE_URL}/tasks"


class MemoryQueryResponse(BaseModel):
    """
    Response for the memory query endpoint.

    Args:
        context: The textual context relevant for the query.
    """

    context: str


class MemoryUpdateResponse(BaseModel):
    task_id: str
    memory_id: Optional[str] = None
    conversation_id: Optional[str] = None
    error: Optional[str] = None


class ApiHeaders(BaseModel):
    api_key: str = Field(alias="X-LumenBrain-ApiKey")

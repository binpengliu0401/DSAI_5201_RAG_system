from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class SubmitQueryMessage(BaseModel):
    type: Literal["submit_query"]
    query: str = Field(min_length=1)


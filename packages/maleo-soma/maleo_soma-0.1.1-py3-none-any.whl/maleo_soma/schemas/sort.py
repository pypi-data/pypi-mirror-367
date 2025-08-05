from __future__ import annotations
from pydantic import BaseModel, Field
from maleo_soma.enums.sort import SortOrder


class SortColumn(BaseModel):
    name: str = Field(..., description="Column name.")
    order: SortOrder = Field(..., description="Sort order.")

from pydantic import BaseModel, Field
from maleo_soma.types.base import OptionalDatetime


class DateFilter(BaseModel):
    name: str = Field(..., description="Column's name")
    from_date: OptionalDatetime = Field(None, description="From date.")
    to_date: OptionalDatetime = Field(None, description="To date.")

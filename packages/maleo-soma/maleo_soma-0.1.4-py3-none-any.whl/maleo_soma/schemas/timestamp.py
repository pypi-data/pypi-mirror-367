from datetime import datetime
from pydantic import BaseModel, Field


class RequestTimestamp(BaseModel):
    requested_at: datetime = Field(..., description="requested_at timestamp")


class ResponseTimestamp(BaseModel):
    responded_at: datetime = Field(..., description="responded_at timestamp")

from pydantic import BaseModel, Field


class OperationSummary(BaseModel):
    summary: str = Field(..., description="Operation's summary")

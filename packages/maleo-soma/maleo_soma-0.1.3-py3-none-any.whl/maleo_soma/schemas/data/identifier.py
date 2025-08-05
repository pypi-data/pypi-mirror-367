from pydantic import BaseModel, Field
from uuid import UUID


class DataIdentifier(BaseModel):
    id: int = Field(..., ge=1, description="Data's ID, must be >= 1.")
    uuid: UUID = Field(..., description="Data's UUID.")

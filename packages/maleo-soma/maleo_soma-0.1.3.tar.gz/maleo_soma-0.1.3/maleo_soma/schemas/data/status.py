from pydantic import BaseModel, Field
from maleo_soma.enums.status import DataStatus as DataStatusEnum


class DataStatus(BaseModel):
    status: DataStatusEnum = Field(..., description="Data's status")

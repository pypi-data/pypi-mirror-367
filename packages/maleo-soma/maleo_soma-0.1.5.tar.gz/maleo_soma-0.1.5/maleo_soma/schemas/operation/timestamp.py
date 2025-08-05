from datetime import datetime, timezone
from pydantic import BaseModel, Field, model_validator
from typing import Self
from maleo_soma.schemas.mixin import OptionalDuration
from maleo_soma.types.base import OptionalDatetime


class ExecutionTimestamp(BaseModel):
    executed_at: datetime = Field(..., description="executed_at timestamp")


class OptionalCompletionTimestamp(BaseModel):
    completed_at: OptionalDatetime = Field(..., description="completed_at timestamp")


class OperationTimestamp(
    OptionalDuration, OptionalCompletionTimestamp, ExecutionTimestamp
):
    @model_validator(mode="after")
    def calculate_duration(self) -> Self:
        if self.completed_at is not None:
            self.duration = (self.completed_at - self.executed_at).total_seconds()
        else:
            self.duration = None
        return self

    @classmethod
    def now(cls) -> "OperationTimestamp":
        return cls(
            executed_at=datetime.now(tz=timezone.utc), completed_at=None, duration=0
        )


class OperationTimestampMixin(BaseModel):
    timestamp: OperationTimestamp = Field(..., description="Operation's timestamp")

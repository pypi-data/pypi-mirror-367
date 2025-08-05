from datetime import datetime
from pydantic import BaseModel, Field
from maleo_soma.types.base import OptionalDatetime


class CreationTimestamp(BaseModel):
    created_at: datetime = Field(..., description="created_at timestamp")


class UpdateTimestamp(BaseModel):
    updated_at: datetime = Field(..., description="updated_at timestamp")


class LifecyleTimestamp(UpdateTimestamp, CreationTimestamp):
    pass


class OptionalDeletionTimestamp(BaseModel):
    deleted_at: OptionalDatetime = Field(None, description="deleted_at timestamp")


class OptionalRestorationTimestamp(BaseModel):
    restored_at: OptionalDatetime = Field(None, description="restored_at timestamp")


class OptionalDeactivationTimestamp(BaseModel):
    deactivated_at: OptionalDatetime = Field(
        None, description="deactivated_at timestamp"
    )


class ActivationTimestamp(BaseModel):
    activated_at: datetime = Field(..., description="activated_at timestamp")


class StatusTimestamp(
    ActivationTimestamp,
    OptionalDeactivationTimestamp,
    OptionalRestorationTimestamp,
    OptionalDeletionTimestamp,
):
    pass


class DataTimestamp(StatusTimestamp, LifecyleTimestamp):
    pass

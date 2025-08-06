from typing import Optional
from pydantic import BaseModel, Field
from maleo_soma.types.base import OptionalStringToAnyDict
from .identifier import ResourceIdentifier


class Resource(BaseModel):
    identifier: ResourceIdentifier = Field(..., description="Identifier")
    details: OptionalStringToAnyDict = Field(None, description="Details")


class ResourceMixin(BaseModel):
    resource: Resource = Field(..., description="Resource")


class OptionalResourceMixin(BaseModel):
    resource: Optional[Resource] = Field(None, description="Resource. (Optional)")

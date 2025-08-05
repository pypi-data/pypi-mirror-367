from pydantic import BaseModel, Field
from maleo_soma.types.base import OptionalBoolean, OptionalInteger


class IsDefault(BaseModel):
    is_default: OptionalBoolean = Field(None, description="Whether data is default")


class IsRoot(BaseModel):
    is_root: OptionalBoolean = Field(None, description="Whether data is root")


class IsParent(BaseModel):
    is_parent: OptionalBoolean = Field(None, description="Whether data is parent")


class IsChild(BaseModel):
    is_child: OptionalBoolean = Field(None, description="Whether data is child")


class IsLeaf(BaseModel):
    is_leaf: OptionalBoolean = Field(None, description="Whether data is leaf")


class Order(BaseModel):
    order: OptionalInteger = Field(..., description="Data's order")

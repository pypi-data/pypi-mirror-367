from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Union
from maleo_soma.types.base import OptionalBoolean, OptionalInteger


class Order(BaseModel):
    order: OptionalInteger = Field(..., description="Order")


CodeT = TypeVar("CodeT", bound=Union[str, StrEnum])


class Code(BaseModel, Generic[CodeT]):
    code: CodeT = Field(..., description="Code")


class Key(BaseModel):
    key: str = Field(..., description="Key")


class Name(BaseModel):
    name: str = Field(..., description="Name")


class IsDefault(BaseModel):
    is_default: OptionalBoolean = Field(None, description="Whether is default")


class IsRoot(BaseModel):
    is_root: OptionalBoolean = Field(None, description="Whether is root")


class IsParent(BaseModel):
    is_parent: OptionalBoolean = Field(None, description="Whether is parent")


class IsChild(BaseModel):
    is_child: OptionalBoolean = Field(None, description="Whether is child")


class IsLeaf(BaseModel):
    is_leaf: OptionalBoolean = Field(None, description="Whether is leaf")

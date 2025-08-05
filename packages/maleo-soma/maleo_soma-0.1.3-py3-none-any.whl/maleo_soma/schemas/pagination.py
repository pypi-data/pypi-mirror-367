from pydantic import BaseModel, Field
from typing import Any, Optional, Union
from maleo_soma.enums.pagination import Limit


class Page(BaseModel):
    page: int = Field(1, ge=1, description="Page number, must be >= 1.")


class FlexibleLimit(BaseModel):
    limit: Optional[Limit] = Field(None, description="Page limit. (Optional)")


class StrictLimit(BaseModel):
    limit: Limit = Field(Limit.LIM_10, description="Page limit.")


class PageInfo(BaseModel):
    data_count: int = Field(..., description="Fetched data count")
    total_data: int = Field(..., description="Total data count")
    total_pages: int = Field(..., description="Total pages count")


class BasePaginationSchema(BaseModel):
    pass


class BaseFlexiblePagination(FlexibleLimit, Page, BasePaginationSchema):
    pass


class FlexiblePagination(PageInfo, BaseFlexiblePagination):
    pass


class BaseStrictPagination(StrictLimit, Page, BasePaginationSchema):
    pass


class StrictPagination(PageInfo, BaseStrictPagination):
    pass


# ! Do not instantiate and use this class
# * This class is created for future type override
class AnyPaginationMixin(BaseModel):
    pagination: Any = Field(..., description="Pagination")


class NoPaginationMixin(AnyPaginationMixin):
    pagination: None = None


type PaginationT = Union[FlexiblePagination, StrictPagination]
type OptionalPaginationT = Optional[PaginationT]


class PaginationMixin(AnyPaginationMixin):
    pagination: PaginationT = Field(..., description="Pagination")


class OptionalPaginationMixin(AnyPaginationMixin):
    pagination: OptionalPaginationT = Field(None, description="Pagination. (Optional)")

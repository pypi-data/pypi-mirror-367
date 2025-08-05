from pydantic import BaseModel, Field
from typing import Any, Generic, List, Optional
from maleo_soma.schemas.data import DataT, DataMixin, DataPair, OldDataT, NewDataT
from maleo_soma.schemas.result.descriptor import (
    ResultDescriptorSchema,
    AnyDataResultDescriptorSchema,
    NoDataResultDescriptorSchema,
    CreateSingleDataResultDescriptorSchema,
    ReadSingleDataResultDescriptorSchema,
    UpdateSingleDataResultDescriptorSchema,
    DeleteSingleDataResultDescriptorSchema,
    CreateMultipleDataResultDescriptorSchema,
    ReadMultipleDataResultDescriptorSchema,
    UpdateMultipleDataResultDescriptorSchema,
    DeleteMultipleDataResultDescriptorSchema,
)
from maleo_soma.schemas.metadata import OptionalMetadataMixin, MetadataT
from maleo_soma.schemas.mixin import OptionalOther
from maleo_soma.schemas.pagination import (
    AnyPaginationMixin,
    NoPaginationMixin,
    OptionalPaginationMixin,
)


class ResourceOperationResultSchema(
    OptionalOther,
    OptionalMetadataMixin[MetadataT],
    AnyPaginationMixin,
    DataMixin[DataPair[OldDataT, NewDataT]],
    ResultDescriptorSchema,
    BaseModel,
    Generic[OldDataT, NewDataT, MetadataT],
):
    pass


class AnyDataResourceOperationResult(
    AnyDataResultDescriptorSchema,
    ResourceOperationResultSchema[Any, Any, MetadataT],
    Generic[MetadataT],
):
    pass


class AnyDataResourceOperationResultMixin(Generic[MetadataT]):
    result: AnyDataResourceOperationResult[MetadataT] = Field(..., description="Result")


class NoDataResourceOperationResult(
    NoPaginationMixin,
    NoDataResultDescriptorSchema,
    ResourceOperationResultSchema[None, None, MetadataT],
    Generic[MetadataT],
):
    pass


class NoDataResourceOperationResultMixin(Generic[MetadataT]):
    result: NoDataResourceOperationResult[MetadataT] = Field(..., description="Result")


class CreateSingleResourceOperationResult(
    NoPaginationMixin,
    CreateSingleDataResultDescriptorSchema,
    ResourceOperationResultSchema[None, DataT, MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class CreateSingleResourceOperationResultMixin(Generic[DataT, MetadataT]):
    result: CreateSingleResourceOperationResult[DataT, MetadataT] = Field(
        ..., description="Result"
    )


class ReadSingleResourceOperationResult(
    NoPaginationMixin,
    ReadSingleDataResultDescriptorSchema,
    ResourceOperationResultSchema[Optional[DataT], None, MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class ReadSingleResourceOperationResultMixin(Generic[DataT, MetadataT]):
    result: ReadSingleResourceOperationResult[DataT, MetadataT] = Field(
        ..., description="Result"
    )


class UpdateSingleResourceOperationResult(
    NoPaginationMixin,
    UpdateSingleDataResultDescriptorSchema,
    ResourceOperationResultSchema[DataT, DataT, MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class UpdateSingleResourceOperationResultMixin(Generic[DataT, MetadataT]):
    result: UpdateSingleResourceOperationResult[DataT, MetadataT] = Field(
        ..., description="Result"
    )


class DeleteSingleResourceOperationResult(
    NoPaginationMixin,
    DeleteSingleDataResultDescriptorSchema,
    ResourceOperationResultSchema[DataT, None, MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class DeleteSingleResourceOperationResultMixin(Generic[DataT, MetadataT]):
    result: DeleteSingleResourceOperationResult[DataT, MetadataT] = Field(
        ..., description="Result"
    )


class CreateMultipleResourceOperationResult(
    OptionalPaginationMixin,
    CreateMultipleDataResultDescriptorSchema,
    ResourceOperationResultSchema[None, List[DataT], MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class CreateMultipleResourceOperationResultMixin(Generic[DataT, MetadataT]):
    result: CreateMultipleResourceOperationResult[DataT, MetadataT] = Field(
        ..., description="Result"
    )


class ReadMultipleResourceOperationResult(
    OptionalPaginationMixin,
    ReadMultipleDataResultDescriptorSchema,
    ResourceOperationResultSchema[Optional[List[DataT]], None, MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class ReadMultipleResourceOperationResultMixin(Generic[DataT, MetadataT]):
    result: ReadMultipleResourceOperationResult[DataT, MetadataT] = Field(
        ..., description="Result"
    )


class UpdateMultipleResourceOperationResult(
    OptionalPaginationMixin,
    UpdateMultipleDataResultDescriptorSchema,
    ResourceOperationResultSchema[List[DataT], List[DataT], MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class UpdateMultipleResourceOperationResultMixin(Generic[DataT, MetadataT]):
    result: UpdateMultipleResourceOperationResult[DataT, MetadataT] = Field(
        ..., description="Result"
    )


class DeleteMultipleResourceOperationResult(
    OptionalPaginationMixin,
    DeleteMultipleDataResultDescriptorSchema,
    ResourceOperationResultSchema[List[DataT], None, MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class DeleteMultipleResourceOperationResultMixin(Generic[DataT, MetadataT]):
    result: DeleteMultipleResourceOperationResult[DataT, MetadataT] = Field(
        ..., description="Result"
    )

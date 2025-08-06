from pydantic import BaseModel, Field
from typing import Generic, List
from maleo_soma.mixins.general import OptionalOther
from maleo_soma.schemas.data import (
    AnyDataMixin,
    NoDataMixin,
    DataT,
    DataMixin,
    DataPair,
)
from maleo_soma.schemas.result.descriptor import (
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
from maleo_soma.schemas.pagination import (
    AnyPaginationMixin,
    NoPaginationMixin,
    PaginationMixin,
)


class ResourceOperationResultSchema(
    OptionalOther,
    OptionalMetadataMixin[MetadataT],
    AnyPaginationMixin,
    AnyDataMixin,
    AnyDataResultDescriptorSchema,
    BaseModel,
    Generic[MetadataT],
):
    pass


class NoDataResourceOperationResult(
    NoPaginationMixin,
    NoDataMixin,
    NoDataResultDescriptorSchema,
    ResourceOperationResultSchema[MetadataT],
    Generic[MetadataT],
):
    pass


class NoDataResourceOperationResultMixin(Generic[MetadataT]):
    result: NoDataResourceOperationResult[MetadataT] = Field(..., description="Result")


class CreateSingleResourceOperationResult(
    NoPaginationMixin,
    DataMixin[DataPair[None, DataT]],
    CreateSingleDataResultDescriptorSchema,
    ResourceOperationResultSchema[MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class CreateSingleResourceOperationResultMixin(Generic[DataT, MetadataT]):
    result: CreateSingleResourceOperationResult[DataT, MetadataT] = Field(
        ..., description="Result"
    )


class ReadSingleResourceOperationResult(
    NoPaginationMixin,
    DataMixin[DataPair[DataT, None]],
    ReadSingleDataResultDescriptorSchema,
    ResourceOperationResultSchema[MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class ReadSingleResourceOperationResultMixin(Generic[DataT, MetadataT]):
    result: ReadSingleResourceOperationResult[DataT, MetadataT] = Field(
        ..., description="Result"
    )


class UpdateSingleResourceOperationResult(
    NoPaginationMixin,
    DataMixin[DataPair[DataT, DataT]],
    UpdateSingleDataResultDescriptorSchema,
    ResourceOperationResultSchema[MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class UpdateSingleResourceOperationResultMixin(Generic[DataT, MetadataT]):
    result: UpdateSingleResourceOperationResult[DataT, MetadataT] = Field(
        ..., description="Result"
    )


class DeleteSingleResourceOperationResult(
    NoPaginationMixin,
    DataMixin[DataPair[DataT, None]],
    DeleteSingleDataResultDescriptorSchema,
    ResourceOperationResultSchema[MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class DeleteSingleResourceOperationResultMixin(Generic[DataT, MetadataT]):
    result: DeleteSingleResourceOperationResult[DataT, MetadataT] = Field(
        ..., description="Result"
    )


class CreateMultipleResourceOperationResult(
    PaginationMixin,
    DataMixin[DataPair[None, List[DataT]]],
    CreateMultipleDataResultDescriptorSchema,
    ResourceOperationResultSchema[MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class CreateMultipleResourceOperationResultMixin(Generic[DataT, MetadataT]):
    result: CreateMultipleResourceOperationResult[DataT, MetadataT] = Field(
        ..., description="Result"
    )


class ReadMultipleResourceOperationResult(
    PaginationMixin,
    DataMixin[DataPair[List[DataT], None]],
    ReadMultipleDataResultDescriptorSchema,
    ResourceOperationResultSchema[MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class ReadMultipleResourceOperationResultMixin(Generic[DataT, MetadataT]):
    result: ReadMultipleResourceOperationResult[DataT, MetadataT] = Field(
        ..., description="Result"
    )


class UpdateMultipleResourceOperationResult(
    PaginationMixin,
    DataMixin[DataPair[List[DataT], List[DataT]]],
    UpdateMultipleDataResultDescriptorSchema,
    ResourceOperationResultSchema[MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class UpdateMultipleResourceOperationResultMixin(Generic[DataT, MetadataT]):
    result: UpdateMultipleResourceOperationResult[DataT, MetadataT] = Field(
        ..., description="Result"
    )


class DeleteMultipleResourceOperationResult(
    PaginationMixin,
    DataMixin[DataPair[List[DataT], None]],
    DeleteMultipleDataResultDescriptorSchema,
    ResourceOperationResultSchema[MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class DeleteMultipleResourceOperationResultMixin(Generic[DataT, MetadataT]):
    result: DeleteMultipleResourceOperationResult[DataT, MetadataT] = Field(
        ..., description="Result"
    )

import traceback as tb
from typing import Optional, Union
from uuid import UUID
from maleo_soma.schemas.authentication import Authentication
from maleo_soma.schemas.error import (
    ErrorSchema,
    BadRequestErrorSchema,
    UnauthorizedErrorSchema,
    ForbiddenErrorSchema,
    NotFoundErrorSchema,
    MethodNotAllowedErrorSchema,
    UnprocessableEntityErrorSchema,
    TooManyRequestsErrorSchema,
    InternalServerErrorSchema,
    DatabaseErrorSchema,
    NotImplementedErrorSchema,
    BadGatewayErrorSchema,
    ServiceUnavailableErrorSchema,
)
from maleo_soma.schemas.error.spec import (
    ErrorSpecSchema,
    BadRequestErrorSpecSchema,
    UnauthorizedErrorSpecSchema,
    ForbiddenErrorSpecSchema,
    NotFoundErrorSpecSchema,
    MethodNotAllowedErrorSpecSchema,
    UnprocessableEntityErrorSpecSchema,
    TooManyRequestsErrorSpecSchema,
    InternalServerErrorSpecSchema,
    DatabaseErrorSpecSchema,
    NotImplementedErrorSpecSchema,
    BadGatewayErrorSpecSchema,
    ServiceUnavailableErrorSpecSchema,
)
from maleo_soma.schemas.operation.context import OperationContextSchema
from maleo_soma.schemas.operation.resource import (
    CreateFailedResourceOperationSchema,
    DeleteFailedResourceOperationSchema,
    ReadFailedResourceOperationSchema,
    UpdateFailedResourceOperationSchema,
    generate_failed_resource_operation,
)
from maleo_soma.schemas.operation.resource.action import AllResourceOperationAction
from maleo_soma.schemas.operation.system import FailedSystemOperationSchema
from maleo_soma.schemas.operation.system.action import SystemOperationActionSchema
from maleo_soma.schemas.operation.timestamp import OperationTimestamp
from maleo_soma.schemas.request import RequestContext
from maleo_soma.schemas.service import ServiceContext
from maleo_soma.types.base import ListOfStrings, OptionalAny, StringToAnyDict


class Error(Exception):
    """Base class for all exceptions raised by Maleo"""

    spec: ErrorSpecSchema

    def __init__(
        self,
        *args: object,
        service_context: Optional[ServiceContext],
        operation_id: UUID,
        operation_context: OperationContextSchema,
        operation_timestamp: OperationTimestamp,
        operation_summary: str,
        operation_action: Union[
            AllResourceOperationAction,
            SystemOperationActionSchema,
        ],
        request_context: Optional[RequestContext],
        authentication: Optional[Authentication],
        details: OptionalAny = None,
    ) -> None:
        super().__init__(*args)
        self.service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )
        self.operation_id = operation_id
        self.operation_context = operation_context
        self.operation_timestamp = (
            operation_timestamp
            if operation_timestamp is not None
            else OperationTimestamp.now()
        )
        self.operation_summary = operation_summary
        self.request_context = request_context
        self.authentication = authentication
        self.operation_action = operation_action
        self.details = details

    @property
    def traceback(self) -> ListOfStrings:
        return tb.format_exception(self)

    @property
    def _schema_dict(self) -> StringToAnyDict:
        return {
            **self.spec.model_dump(),
            "details": self.details,
            "traceback": self.traceback,
        }

    @property
    def schema(self) -> ErrorSchema:
        return ErrorSchema.model_validate(self._schema_dict)

    @property
    def operation_schema(self) -> Union[
        CreateFailedResourceOperationSchema,
        ReadFailedResourceOperationSchema,
        UpdateFailedResourceOperationSchema,
        DeleteFailedResourceOperationSchema,
        FailedSystemOperationSchema,
    ]:
        if isinstance(self.operation_action, SystemOperationActionSchema):
            return FailedSystemOperationSchema(
                service_context=self.service_context,
                id=self.operation_id,
                context=self.operation_context,
                timestamp=self.operation_timestamp,
                summary="Failed system operation",
                error=self.schema,
                request_context=self.request_context,
                authentication=self.authentication,
                action=self.operation_action,
            )
        else:
            return generate_failed_resource_operation(
                action=self.operation_action,
                service_context=self.service_context,
                id=self.operation_id,
                context=self.operation_context,
                timestamp=self.operation_timestamp,
                summary=self.operation_summary,
                error=self.schema,
                request_context=self.request_context,
                authentication=self.authentication,
            )


class ClientError(Error):
    """Base class for all client error (HTTP 4xx) responses"""


class BadRequest(ClientError):
    spec = BadRequestErrorSpecSchema()

    @property
    def schema(self) -> BadRequestErrorSchema:
        return BadRequestErrorSchema.model_validate(self._schema_dict)


class Unauthorized(ClientError):
    spec = UnauthorizedErrorSpecSchema()

    @property
    def schema(self) -> UnauthorizedErrorSchema:
        return UnauthorizedErrorSchema.model_validate(self._schema_dict)


class Forbidden(ClientError):
    spec = ForbiddenErrorSpecSchema()

    @property
    def schema(self) -> ForbiddenErrorSchema:
        return ForbiddenErrorSchema.model_validate(self._schema_dict)


class NotFound(ClientError):
    spec = NotFoundErrorSpecSchema()

    @property
    def schema(self) -> NotFoundErrorSchema:
        return NotFoundErrorSchema.model_validate(self._schema_dict)


class MethodNotAllowed(ClientError):
    spec = MethodNotAllowedErrorSpecSchema()

    @property
    def schema(self) -> MethodNotAllowedErrorSchema:
        return MethodNotAllowedErrorSchema.model_validate(self._schema_dict)


class UnprocessableEntity(ClientError):
    spec = UnprocessableEntityErrorSpecSchema()

    @property
    def schema(self) -> UnprocessableEntityErrorSchema:
        return UnprocessableEntityErrorSchema.model_validate(self._schema_dict)


class TooManyRequests(ClientError):
    spec = TooManyRequestsErrorSpecSchema()

    @property
    def schema(self) -> TooManyRequestsErrorSchema:
        return TooManyRequestsErrorSchema.model_validate(self._schema_dict)


class ServerError(Error):
    """Base class for all server error (HTTP 5xx) responses"""


class InternalServerError(ServerError):
    spec = InternalServerErrorSpecSchema()

    @property
    def schema(self) -> InternalServerErrorSchema:
        return InternalServerErrorSchema.model_validate(self._schema_dict)


class DatabaseError(InternalServerError):
    spec = DatabaseErrorSpecSchema()

    @property
    def schema(self) -> DatabaseErrorSchema:
        return DatabaseErrorSchema.model_validate(self._schema_dict)


class NotImplemented(ServerError):
    spec = NotImplementedErrorSpecSchema()

    @property
    def schema(self) -> NotImplementedErrorSchema:
        return NotImplementedErrorSchema.model_validate(self._schema_dict)


class BadGateway(ServerError):
    spec = BadGatewayErrorSpecSchema()

    @property
    def schema(self) -> BadGatewayErrorSchema:
        return BadGatewayErrorSchema.model_validate(self._schema_dict)


class ServiceUnavailable(ServerError):
    spec = ServiceUnavailableErrorSpecSchema()

    @property
    def schema(self) -> ServiceUnavailableErrorSchema:
        return ServiceUnavailableErrorSchema.model_validate(self._schema_dict)

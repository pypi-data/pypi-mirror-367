from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, APIRouter
from fastapi.exceptions import RequestValidationError
from google.cloud import pubsub_v1
from google.oauth2.service_account import Credentials
from redis.asyncio.client import Redis
from redis.exceptions import RedisError
from starlette.exceptions import HTTPException
from starlette.types import Lifespan, AppType
from sqlalchemy import MetaData
from typing import Optional
from uuid import UUID, uuid4
from maleo_soma.dtos.configurations import (
    ConfigurationDTO,
    LoggerDTO,
)
from maleo_soma.dtos.configurations.pubsub.publisher import (
    AdditionalTopicsConfigurationDTO,
)
from maleo_soma.dtos.credential import MaleoCredentialDTO
from maleo_soma.dtos.settings import Settings
from maleo_soma.enums.environment import Environment
from maleo_soma.enums.logging import LogLevel
from maleo_soma.enums.operation import (
    OperationLayer,
    OperationOrigin,
    OperationTarget,
    SystemOperationType,
)
from maleo_soma.enums.secret import SecretFormat
from maleo_soma.exceptions import Error, InternalServerError
from maleo_soma.managers.cache import CacheManagers
from maleo_soma.managers.db import DatabaseManager
from maleo_soma.managers.client.google.storage import GoogleCloudStorage
from maleo_soma.managers.client.google.secret import GoogleSecretManager
from maleo_soma.managers.middleware import MiddlewareManager
from maleo_soma.schemas.key.rsa import Complete
from maleo_soma.schemas.operation.context import (
    OperationContextSchema,
    generate_operation_context,
)
from maleo_soma.schemas.operation.system import (
    SuccessfulSystemOperationSchema,
)
from maleo_soma.schemas.operation.system.action import SystemOperationActionSchema
from maleo_soma.schemas.operation.timestamp import OperationTimestamp
from maleo_soma.schemas.service import ServiceContext
from maleo_soma.schemas.token import CredentialPayload
from maleo_soma.types.base import OptionalString, OptionalUUID
from maleo_soma.utils.exceptions.request import (
    http_exception_handler,
    maleo_exception_handler,
    validation_exception_handler,
)
from maleo_soma.utils.loaders.yaml import from_path, from_string
from maleo_soma.utils.logging import (
    SimpleConfig,
    ApplicationLogger,
    CacheLogger,
    DatabaseLogger,
    MiddlewareLogger,
    RepositoryLogger,
    ServiceLogger,
)
from maleo_soma.utils.name import get_fully_qualified_name
from maleo_soma.utils.token import encode


class ServiceManager:
    """ServiceManager class"""

    key = "service_manager"
    name = "ServiceManager"

    def __init__(
        self,
        db_metadata: MetaData,
        google_credentials: Credentials,
        log_config: SimpleConfig,
        settings: Settings,
        secret_manager: GoogleSecretManager,
        additional_topics_configurations: Optional[
            AdditionalTopicsConfigurationDTO
        ] = None,
        operation_id: OptionalUUID = None,
    ):
        self._db_metadata = db_metadata  # Declare DB Metadata
        self._google_credentials = google_credentials  # Declare googlr credentials
        self._log_config = log_config  # Declare log config
        self._settings = settings  # Initialize settings
        self._secret_manager = secret_manager  # Initialize secret manager

        # Initialize Service Context
        self._service_context = ServiceContext.from_settings(self._settings)
        operation_id = operation_id if operation_id is not None else uuid4()

        operation_context = generate_operation_context(
            origin=OperationOrigin.SERVICE,
            layer=OperationLayer.UTILITY,
            layer_details={
                "component": {"key": self.key, "name": self.name},
            },
            target=OperationTarget.INTERNAL,
            target_details={"fully_qualified_name": get_fully_qualified_name()},
        )

        operation_action = SystemOperationActionSchema(
            type=SystemOperationType.INITIALIZATION,
            details={
                "type": "manager_initialization",
                "manager_key": self.key,
                "manager_name": self.name,
            },
        )

        executed_at = datetime.now(tz=timezone.utc)

        self._initialize_loggers()

        try:
            self._load_maleo_credentials(operation_id=operation_id)
            self._load_configuration(
                operation_id=operation_id,
                operation_context=operation_context,
                additional_topics_configurations=additional_topics_configurations,
            )
            self._load_keys(
                operation_id=operation_id, operation_context=operation_context
            )
            self._initialize_database_manager(operation_id=operation_id)
            self._initialize_publisher()
            completed_at = datetime.now(tz=timezone.utc)
            SuccessfulSystemOperationSchema(
                service_context=self._service_context,
                id=operation_id,
                context=operation_context,
                timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                summary=f"Successfully initialized {self.name}",
                request_context=None,
                authentication=None,
                action=operation_action,
                result=None,
            ).log(logger=self._loggers.application, level=LogLevel.INFO)
        except Error:
            raise
        except Exception as e:
            completed_at = datetime.now(tz=timezone.utc)
            raise InternalServerError(
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=operation_context,
                operation_timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                operation_summary=f"Exception raised when initializing {self.name}",
                request_context=None,
                authentication=None,
                operation_action=operation_action,
                details=str(e),
            ) from e

    @property
    def log_config(self) -> SimpleConfig:
        return self._log_config

    @property
    def settings(self) -> Settings:
        return self._settings

    def _initialize_loggers(self) -> None:
        application = ApplicationLogger(
            environment=self.settings.ENVIRONMENT,
            service_key=self.settings.SERVICE_KEY,
            **self._log_config.model_dump(),
        )
        cache = CacheLogger(
            environment=self.settings.ENVIRONMENT,
            service_key=self.settings.SERVICE_KEY,
            **self._log_config.model_dump(),
        )
        database = DatabaseLogger(
            environment=self.settings.ENVIRONMENT,
            service_key=self.settings.SERVICE_KEY,
            **self._log_config.model_dump(),
        )
        middleware = MiddlewareLogger(
            environment=self.settings.ENVIRONMENT,
            service_key=self.settings.SERVICE_KEY,
            **self._log_config.model_dump(),
        )
        repository = RepositoryLogger(
            environment=self.settings.ENVIRONMENT,
            service_key=self.settings.SERVICE_KEY,
            **self._log_config.model_dump(),
        )
        service = ServiceLogger(
            environment=self.settings.ENVIRONMENT,
            service_key=self.settings.SERVICE_KEY,
            **self._log_config.model_dump(),
        )
        self._loggers = LoggerDTO(
            application=application,
            cache=cache,
            database=database,
            middleware=middleware,
            repository=repository,
            service=service,
        )

    @property
    def loggers(self) -> LoggerDTO:
        return self._loggers

    def _load_maleo_credentials(self, operation_id: UUID) -> None:
        name = f"maleo-internal-credentials-{self._settings.ENVIRONMENT}"
        read_secret = self._secret_manager.read(
            SecretFormat.STRING, name=name, operation_id=operation_id
        )
        if read_secret.data.old is None:
            raise ValueError("Maleo credential not found")
        data = from_string(read_secret.data.old.value)
        self._maleo_credentials = MaleoCredentialDTO.model_validate(data)

    @property
    def maleo_credentials(self) -> MaleoCredentialDTO:
        return self._maleo_credentials

    def _load_configuration(
        self,
        operation_id: UUID,
        operation_context: OperationContextSchema,
        additional_topics_configurations: Optional[AdditionalTopicsConfigurationDTO],
    ) -> None:
        use_local = self._settings.USE_LOCAL_CONFIGURATIONS
        config_path = self._settings.CONFIGURATIONS_PATH

        if use_local and config_path is not None and isinstance(config_path, str):
            config_path = Path(config_path)
            if config_path.exists() and config_path.is_file():
                data = from_path(config_path)
                self.configurations = ConfigurationDTO.model_validate(data)
                self.configurations.pubsub.publisher.topics.additional = (
                    additional_topics_configurations
                )
                return

        name = (
            f"{self._settings.SERVICE_KEY}-configurations-{self._settings.ENVIRONMENT}"
        )
        read_secret = self._secret_manager.read(
            SecretFormat.STRING, name=name, operation_id=operation_id
        )
        if read_secret.data.old is None:
            raise ValueError(f"Service configuration '{name}' not found")

        data = from_string(read_secret.data.old.value)
        self.configurations = ConfigurationDTO.model_validate(data)
        self.configurations.pubsub.publisher.topics.additional = (
            additional_topics_configurations
        )

    def _load_keys(
        self, operation_id: UUID, operation_context: OperationContextSchema
    ) -> None:
        if self.settings.KEY_PASSWORD is not None:
            password = self.settings.KEY_PASSWORD
        else:
            read_key_password = self._secret_manager.read(
                SecretFormat.STRING, name="maleo-key-password"
            )
            if read_key_password.data.old is None:
                raise ValueError("Key password not found")
            password = read_key_password.data.old.value

        if self.settings.PRIVATE_KEY is not None:
            private = self.settings.PRIVATE_KEY
        else:
            read_private_key = self._secret_manager.read(
                SecretFormat.STRING, name="maleo-private-key"
            )
            if read_private_key.data.old is None:
                raise ValueError("Private key not found")
            private = read_private_key.data.old.value

        if self.settings.PUBLIC_KEY is not None:
            public = self.settings.PUBLIC_KEY
        else:
            read_public_key = self._secret_manager.read(
                SecretFormat.STRING, name="maleo-public-key"
            )
            if read_public_key.data.old is None:
                raise ValueError("Public key not found")
            public = read_public_key.data.old.value

        self._keys = Complete(password=password, private=private, public=public)

    @property
    def keys(self) -> Complete:
        return self._keys

    async def _clear_cache(self) -> None:
        prefixes = [
            self.settings.SERVICE_KEY,
            f"google-cloud-storage:{self.settings.SERVICE_KEY}",
        ]
        for prefix in prefixes:
            async for key in self._redis.scan_iter(f"{prefix}*"):
                await self._redis.delete(key)

    async def check_redis_connection(self) -> bool:
        try:
            await self._redis.ping()
            self._loggers.cache.info("Redis connection check successful.")
            return True
        except RedisError as e:
            self._loggers.cache.error(
                f"Redis connection check failed: {e}", exc_info=True
            )
            return False

    async def initialize_cache(self) -> None:
        if self.configurations.cache.redis is None:
            raise ValueError("Can not find redis configuration")
        self._redis = Redis(
            host=self.configurations.cache.redis.host,
            port=self.configurations.cache.redis.port,
            db=self.configurations.cache.redis.db,
            password=self.configurations.cache.redis.password,
            decode_responses=self.configurations.cache.redis.decode_responses,
            health_check_interval=self.configurations.cache.redis.health_check_interval,
        )
        await self.check_redis_connection()
        self._cache = CacheManagers(redis=self._redis)
        await self._clear_cache()

    @property
    def redis(self) -> Redis:
        return self._redis

    @property
    def cache(self) -> CacheManagers:
        return self._cache

    def initialize_cloud_storage(self, operation_id: OptionalUUID = None) -> None:
        operation_id = operation_id if operation_id is not None else uuid4()
        environment = (
            Environment.STAGING
            if self._settings.ENVIRONMENT == Environment.LOCAL
            else self._settings.ENVIRONMENT
        )
        self._cloud_storage = GoogleCloudStorage(
            log_config=self._log_config,
            service_context=self._service_context,
            operation_id=operation_id,
            bucket_name=f"maleo-suite-{environment}",
            credentials=self._google_credentials,
            redis=self._redis,
        )

    @property
    def cloud_storage(self) -> GoogleCloudStorage:
        return self._cloud_storage

    def _initialize_database_manager(self, operation_id: UUID) -> None:
        self._database_manager = DatabaseManager(
            metadata=self._db_metadata,
            logger=self._loggers.database,
            url=self.configurations.database.url,
            service_context=self._service_context,
            operation_id=operation_id,
        )

    @property
    def database_manager(self) -> DatabaseManager:
        return self._database_manager

    def _initialize_publisher(self) -> None:
        self._publisher = pubsub_v1.PublisherClient()

    @property
    def publisher(self) -> pubsub_v1.PublisherClient:
        return self._publisher

    @property
    def token(self) -> OptionalString:
        credential = CredentialPayload(
            iss=None,
            sub=str(self.maleo_credentials.id),
            sr="administrator",
            u_i=self.maleo_credentials.id,
            u_uu=self.maleo_credentials.uuid,
            u_u=self.maleo_credentials.username,
            u_e=self.maleo_credentials.email,
            u_ut="service",
            o_i=None,
            o_uu=None,
            o_k=None,
            o_ot=None,
            uor=None,
        )
        try:
            token = encode(credential=credential, key=self._keys.private_rsa_key)
            return token
        except Exception:
            return None

    def create_app(
        self,
        router: APIRouter,
        lifespan: Optional[Lifespan[AppType]] = None,
        version: str = "unknown",
        operation_id: OptionalUUID = None,
    ) -> FastAPI:
        operation_id = operation_id if operation_id is not None else uuid4()

        operation_context = generate_operation_context(
            origin=OperationOrigin.SERVICE,
            layer=OperationLayer.UTILITY,
            layer_details={
                "component": {"key": self.key, "name": self.name},
            },
            target=OperationTarget.INTERNAL,
            target_details={"fully_qualified_name": get_fully_qualified_name()},
        )

        operation_action = SystemOperationActionSchema(
            type=SystemOperationType.STARTUP,
            details={"type": "app_creation"},
        )

        executed_at = datetime.now(tz=timezone.utc)

        try:
            root_path = self._settings.ROOT_PATH
            self._app = FastAPI(
                title=self.configurations.service.name,
                version=version,
                lifespan=lifespan,  # type: ignore
                root_path=root_path,
            )

            # Add middleware(s)
            self.middleware_manager = MiddlewareManager(
                self._app,
                configuration=self.configurations.middleware,
                keys=self._keys,
                logger=self._loggers.middleware,
                service_context=self._service_context,
                operation_id=operation_id,
            )
            self.middleware_manager.add(operation_id=operation_id)

            # Add exception handler(s)
            self._app.add_exception_handler(
                exc_class_or_status_code=RequestValidationError,
                handler=validation_exception_handler,  # type: ignore
            )
            self._app.add_exception_handler(
                exc_class_or_status_code=HTTPException,
                handler=http_exception_handler,  # type: ignore
            )
            self._app.add_exception_handler(
                exc_class_or_status_code=Error,
                handler=maleo_exception_handler,  # type: ignore
            )

            # Include router
            self._app.include_router(router)

            completed_at = datetime.now(tz=timezone.utc)
            SuccessfulSystemOperationSchema(
                service_context=self._service_context,
                id=operation_id,
                context=operation_context,
                timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                summary="Successfully created FastAPI application",
                request_context=None,
                authentication=None,
                action=operation_action,
                result=None,
            ).log(logger=self._loggers.application, level=LogLevel.INFO)

            return self._app
        except Error:
            raise
        except Exception as e:
            completed_at = datetime.now(tz=timezone.utc)
            raise InternalServerError(
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=operation_context,
                operation_timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                operation_summary="Exception raised when creating FastAPI application",
                request_context=None,
                authentication=None,
                operation_action=operation_action,
                details=str(e),
            ) from e

    @property
    def app(self) -> FastAPI:
        return self._app

    async def dispose(self, operation_id: OptionalUUID = None) -> None:
        operation_id = operation_id if operation_id is not None else uuid4()

        operation_context = generate_operation_context(
            origin=OperationOrigin.SERVICE,
            layer=OperationLayer.UTILITY,
            layer_details={
                "component": {"key": self.key, "name": self.name},
            },
            target=OperationTarget.INTERNAL,
            target_details={"fully_qualified_name": get_fully_qualified_name()},
        )

        operation_action = SystemOperationActionSchema(
            type=SystemOperationType.DISPOSAL, details=None
        )

        if self._redis is not None:
            await self._redis.close()
        if self._database_manager is not None:
            self._database_manager.dispose()
        if self._loggers is not None:
            self._loggers.application.dispose()
            self._loggers.database.dispose()
            self._loggers.middleware.dispose()

        SuccessfulSystemOperationSchema(
            service_context=self._service_context,
            id=operation_id,
            context=operation_context,
            timestamp=OperationTimestamp(
                executed_at=datetime.now(tz=timezone.utc),
                completed_at=None,
                duration=None,
            ),
            summary="Successfully disposed ServiceManager",
            request_context=None,
            authentication=None,
            action=operation_action,
            result=None,
        ).log(logger=self._loggers.application, level=LogLevel.INFO)

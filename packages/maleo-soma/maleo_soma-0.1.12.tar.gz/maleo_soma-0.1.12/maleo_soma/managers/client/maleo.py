from Crypto.PublicKey.RSA import RsaKey
from pydantic import ConfigDict, Field
from redis.asyncio.client import Redis
from typing import Optional
from maleo_soma.dtos.configurations.cache.redis import RedisCacheNamespaces
from maleo_soma.enums.environment import Environment
from maleo_soma.managers.client.base import (
    ClientManager,
    ClientHTTPControllerManager,
    ClientControllerManagers,
    ClientHTTPController,
    ClientServiceControllers,
    ClientService,
    ClientControllers,
)
from maleo_soma.managers.credential import CredentialManager
from maleo_soma.schemas.operation.context import OperationOriginSchema
from maleo_soma.schemas.service import ServiceContext
from maleo_soma.utils.logging import ClientLogger, SimpleConfig


class MaleoClientHTTPController(ClientHTTPController):
    def __init__(
        self,
        manager: ClientHTTPControllerManager,
        credential_manager: CredentialManager,
    ):
        super().__init__(manager)
        self._credential_manager = credential_manager


class MaleoClientServiceControllers(ClientServiceControllers):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    http: MaleoClientHTTPController = Field(  # type: ignore
        ..., description="Maleo's HTTP Client Controller"
    )


class MaleoClientService(ClientService):
    def __init__(
        self,
        environment: Environment,
        key: str,
        service_context: ServiceContext,
        operation_origin: OperationOriginSchema,
        logger: ClientLogger,
        public_key: RsaKey,
        redis: Redis,
        redis_namespaces: RedisCacheNamespaces,
    ):
        super().__init__(service_context, operation_origin, logger)
        self._environment = environment
        self._key = key
        self._public_key = public_key
        self._redis = redis
        self._redis_namespaces = redis_namespaces


class MaleoClientManager(ClientManager):
    def __init__(
        self,
        environment: Environment,
        key: str,
        name: str,
        url: str,
        log_config: SimpleConfig,
        credential_manager: CredentialManager,
        public_key: RsaKey,
        redis: Redis,
        redis_namespaces: RedisCacheNamespaces,
        service_context: Optional[ServiceContext] = None,
    ):
        super().__init__(
            key,
            name,
            log_config,
            service_context,
        )
        self._environment = environment
        if (
            self._operation_origin.details is not None
            and "identifier" in self._operation_origin.details.keys()
            and isinstance(self._operation_origin.details["identifier"], dict)
        ):
            self._operation_origin.details["identifier"][
                "environment"
            ] = self._environment
        self._url = url
        self._credential_manager = credential_manager
        self._public_key = public_key
        self._redis = redis
        self._redis_namespaces = redis_namespaces

    @property
    def environment(self) -> Environment:
        return self._environment

    def _initialize_controllers(self) -> None:
        # * Initialize managers
        http_controller_manager = ClientHTTPControllerManager(url=self._url)
        self._controller_managers = ClientControllerManagers(
            http=http_controller_manager
        )
        # * Initialize controllers
        #! This initialied an empty controllers. Extend this function in the actual class to initialize all controllers.
        self._controllers = ClientControllers()

    @property
    def controllers(self) -> ClientControllers:
        return self._controllers

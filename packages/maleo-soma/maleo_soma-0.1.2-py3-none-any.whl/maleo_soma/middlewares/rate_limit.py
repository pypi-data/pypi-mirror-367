import asyncio
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4
from maleo_soma.dtos.configurations.middleware import RateLimiterConfigurationDTO
from maleo_soma.enums.logging import LogLevel
from maleo_soma.enums.operation import (
    OperationOrigin,
    OperationLayer,
    OperationTarget,
    SystemOperationType,
)
from maleo_soma.exceptions import InternalServerError
from maleo_soma.schemas.operation.context import generate_operation_context
from maleo_soma.schemas.operation.system import (
    SuccessfulSystemOperationSchema,
)
from maleo_soma.schemas.operation.system.action import SystemOperationActionSchema
from maleo_soma.schemas.operation.timestamp import OperationTimestamp
from maleo_soma.schemas.service import ServiceContext
from maleo_soma.types.base import OptionalUUID
from maleo_soma.utils.logging import MiddlewareLogger
from maleo_soma.utils.name import get_fully_qualified_name


class RateLimiter:
    """RateLimiter class"""

    key = "rate_limiter"
    name = "RateLimiter"

    def __init__(
        self,
        configuration: RateLimiterConfigurationDTO,
        logger: MiddlewareLogger,
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
    ) -> None:
        self._logger = logger
        self._service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )
        operation_id = operation_id if operation_id is not None else uuid4()
        operation_context = generate_operation_context(
            origin=OperationOrigin.SERVICE,
            layer=OperationLayer.MIDDLEWARE,
            layer_details={
                "identifier": {
                    "key": "base_middleware",
                    "name": "Base Middleware",
                },
                "component": {"key": self.key, "name": self.name},
            },
            target=OperationTarget.INTERNAL,
            target_details={"fully_qualified_name": get_fully_qualified_name()},
        )
        operation_action = SystemOperationActionSchema(
            type=SystemOperationType.INITIALIZATION,
            details={
                "type": "class_initialization",
                "class_key": self.key,
                "class_name": self.name,
            },
        )

        self.limit = configuration.limit
        self.window = configuration.window
        self.ip_timeout = configuration.ip_timeout
        self.cleanup_interval = configuration.cleanup_interval
        self._requests: Dict[str, List[datetime]] = defaultdict(list)
        self._last_seen: Dict[str, datetime] = {}
        self._last_cleanup = datetime.now()
        self._lock = asyncio.Lock()

        # Background task management
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        SuccessfulSystemOperationSchema(
            service_context=self._service_context,
            id=operation_id,
            context=operation_context,
            timestamp=OperationTimestamp(
                executed_at=datetime.now(tz=timezone.utc),
                completed_at=None,
                duration=0,
            ),
            summary=f"Successfully initialized {self.name}",
            request_context=None,
            authentication=None,
            action=operation_action,
            result=None,
        ).log(logger=self._logger, level=LogLevel.INFO)

    async def is_rate_limited(self, ip_address: str) -> bool:
        """Check if client IP is rate limited and record the request."""
        async with self._lock:
            now = datetime.now(tz=timezone.utc)
            client_ip = ip_address
            self._last_seen[client_ip] = now

            # Remove old requests outside the window
            self._requests[client_ip] = [
                timestamp
                for timestamp in self._requests[client_ip]
                if (now - timestamp).total_seconds() <= self.window
            ]

            # Check rate limit
            if len(self._requests[client_ip]) >= self.limit:
                return True

            # Record this request
            self._requests[client_ip].append(now)
            return False

    async def cleanup_old_data(self, operation_id: OptionalUUID = None) -> None:
        """Clean up old request data to prevent memory growth."""
        operation_context = generate_operation_context(
            origin=OperationOrigin.SERVICE,
            layer=OperationLayer.MIDDLEWARE,
            layer_details={
                "identifier": {
                    "key": "base_middleware",
                    "name": "Base Middleware",
                },
                "component": {"key": self.key, "name": self.name},
            },
            target=OperationTarget.INTERNAL,
            target_details={"fully_qualified_name": get_fully_qualified_name()},
        )
        async with self._lock:
            if operation_id is None:
                operation_id = uuid4()
            now = datetime.now(tz=timezone.utc)
            inactive_ips = []

            for ip in list(self._requests.keys()):
                # Remove IPs with empty request lists
                if not self._requests[ip]:
                    inactive_ips.append(ip)
                    continue

                # Remove IPs that haven't been active recently
                last_active = self._last_seen.get(ip, datetime.min)
                if (now - last_active).total_seconds() > self.ip_timeout:
                    inactive_ips.append(ip)

            # Clean up inactive IPs
            for ip in inactive_ips:
                self._requests.pop(ip, None)
                self._last_seen.pop(ip, None)

            completed_at = datetime.now(tz=timezone.utc)
            SuccessfulSystemOperationSchema(
                service_context=self._service_context,
                id=operation_id,
                context=operation_context,
                timestamp=OperationTimestamp(
                    executed_at=now,
                    completed_at=completed_at,
                    duration=(completed_at - now).total_seconds(),
                ),
                summary="Successfully cleaned up old data in RateLimiter",
                request_context=None,
                authentication=None,
                action=SystemOperationActionSchema(
                    type=SystemOperationType.BACKGROUND_JOB, details=None
                ),
                result=None,
            ).log(logger=self._logger, level=LogLevel.INFO)

    async def start_cleanup_task(self, operation_id: OptionalUUID = None):
        """Start the background cleanup task"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._shutdown_event.clear()  # Reset shutdown event
            self._cleanup_task = asyncio.create_task(self._background_cleanup())

    async def stop_cleanup_task(self):
        """Stop the background cleanup task"""
        self._shutdown_event.set()
        if self._cleanup_task and not self._cleanup_task.done():
            try:
                await asyncio.wait_for(self._cleanup_task, timeout=5.0)
            except asyncio.TimeoutError:
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass

    async def _background_cleanup(self):
        """Background task that runs cleanup periodically"""
        operation_context = generate_operation_context(
            origin=OperationOrigin.SERVICE,
            layer=OperationLayer.MIDDLEWARE,
            layer_details={
                "identifier": {
                    "key": "base_middleware",
                    "name": "Base Middleware",
                },
                "component": {"key": self.key, "name": self.name},
            },
            target=OperationTarget.INTERNAL,
            target_details={"fully_qualified_name": get_fully_qualified_name()},
        )
        operation_action = SystemOperationActionSchema(
            type=SystemOperationType.BACKGROUND_JOB, details=None
        )
        while not self._shutdown_event.is_set():
            operation_id = uuid4()
            try:
                await asyncio.sleep(self.cleanup_interval)
                if not self._shutdown_event.is_set():
                    await self.cleanup_old_data(operation_id)
            except asyncio.CancelledError:
                break
            except Exception as e:
                InternalServerError(
                    service_context=self._service_context,
                    operation_id=operation_id,
                    operation_context=operation_context,
                    operation_timestamp=OperationTimestamp.now(),
                    operation_summary="Exception raised when performing RateLimiter background cleanup",
                    request_context=None,
                    authentication=None,
                    operation_action=operation_action,
                    details=str(e),
                ).operation_schema.log(logger=self._logger, level=LogLevel.ERROR)

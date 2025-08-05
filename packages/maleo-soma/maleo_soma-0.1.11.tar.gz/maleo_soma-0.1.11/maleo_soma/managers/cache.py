from redis.asyncio.client import Redis
from redis.exceptions import RedisError
from maleo_soma.dtos.configurations.cache import CacheConfigurationDTO
from maleo_soma.dtos.settings import Settings


class CacheManager:
    def __init__(
        self, settings: Settings, configurations: CacheConfigurationDTO
    ) -> None:
        self.settings = settings
        if configurations.redis is None:
            raise ValueError("Can not find redis configuration")
        self.redis = Redis(
            host=configurations.redis.host,
            port=configurations.redis.port,
            db=configurations.redis.db,
            password=configurations.redis.password,
            decode_responses=configurations.redis.decode_responses,
            health_check_interval=configurations.redis.health_check_interval,
        )

    @classmethod
    async def new(
        cls, settings: Settings, configurations: CacheConfigurationDTO
    ) -> "CacheManager":
        self = cls(settings, configurations)
        await self.check_redis_connection()
        await self._clear_redis()
        return self

    async def _clear_redis(self) -> None:
        prefixes = [
            self.settings.SERVICE_KEY,
            f"google-cloud-storage:{self.settings.SERVICE_KEY}",
        ]
        for prefix in prefixes:
            async for key in self.redis.scan_iter(f"{prefix}*"):
                await self.redis.delete(key)

    async def check_redis_connection(self) -> bool:
        try:
            await self.redis.ping()
            return True
        except RedisError:
            return False

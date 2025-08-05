from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from .redis import RedisCacheConfigurationDTO


class CacheConfigurationDTO(BaseModel):
    redis: Optional[RedisCacheConfigurationDTO] = Field(
        None, description="Redis cache's configurations"
    )

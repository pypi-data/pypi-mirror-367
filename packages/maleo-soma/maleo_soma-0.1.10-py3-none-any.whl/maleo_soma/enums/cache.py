from enum import StrEnum


class CacheLayer(StrEnum):
    CLIENT = "client"
    REPOSITORY = "repository"
    ROUTER = "router"

from pydantic import BaseModel, Field
from typing import Optional


class TopicConfigurationDTO(BaseModel):
    id: str = Field(..., description="Topic's id")


DEFAULT_DATABASE_OPERATION_TOPIC_CONFIGURATIONS = TopicConfigurationDTO(
    id="database-operation"
)

DEFAULT_OPERATION_TOPIC_CONFIGURATIONS = TopicConfigurationDTO(id="operation")


class MandatoryTopicsConfigurationDTO(BaseModel):
    database_operation: TopicConfigurationDTO = Field(
        default=DEFAULT_DATABASE_OPERATION_TOPIC_CONFIGURATIONS,
        description="Database operation topic configurations",
    )
    operation: TopicConfigurationDTO = Field(
        default=DEFAULT_OPERATION_TOPIC_CONFIGURATIONS,
        description="Operation topic configurations",
    )


class AdditionalTopicsConfigurationDTO(BaseModel):
    pass


class TopicsConfigurationDTO(BaseModel):
    mandatory: MandatoryTopicsConfigurationDTO = Field(
        default_factory=MandatoryTopicsConfigurationDTO,
        description="Mandatory topics configurations",
    )
    additional: Optional[AdditionalTopicsConfigurationDTO] = Field(
        default=None, description="Additional topics configurations"
    )


class PublisherConfigurationDTO(BaseModel):
    topics: TopicsConfigurationDTO = Field(
        default_factory=TopicsConfigurationDTO, description="Topics configurations"
    )

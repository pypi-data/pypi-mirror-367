from pydantic import BaseModel, Field
from typing import Optional
from maleo_soma.enums.environment import Environment
from maleo_soma.enums.service import Service


class MaleoClientConfigurationDTO(BaseModel):
    environment: Environment = Field(..., description="Client's environment")
    key: Service = Field(..., description="Client's key")
    name: str = Field(..., description="Client's name")
    url: str = Field(..., description="Client's URL")


class MaleoClientsConfigurationDTO(BaseModel):
    telemetry: Optional[MaleoClientConfigurationDTO] = Field(
        None, description="MaleoTelemetry client's configuration"
    )
    metadata: Optional[MaleoClientConfigurationDTO] = Field(
        None, description="MaleoMetadata client's configuration"
    )
    identity: Optional[MaleoClientConfigurationDTO] = Field(
        None, description="MaleoIdentity client's configuration"
    )
    access: Optional[MaleoClientConfigurationDTO] = Field(
        None, description="MaleoAccess client's configuration"
    )
    workshop: Optional[MaleoClientConfigurationDTO] = Field(
        None, description="MaleoWorkshop client's configuration"
    )
    soapie: Optional[MaleoClientConfigurationDTO] = Field(
        None, description="MaleoSOAPIE client's configuration"
    )
    medix: Optional[MaleoClientConfigurationDTO] = Field(
        None, description="MaleoMedix client's configuration"
    )
    dicom: Optional[MaleoClientConfigurationDTO] = Field(
        None, description="MaleoDICOM client's configuration"
    )
    scribe: Optional[MaleoClientConfigurationDTO] = Field(
        None, description="MaleoScribe client's configuration"
    )
    cds: Optional[MaleoClientConfigurationDTO] = Field(
        None, description="MaleoCDS client's configuration"
    )
    imaging: Optional[MaleoClientConfigurationDTO] = Field(
        None, description="MaleoImaging client's configuration"
    )
    mcu: Optional[MaleoClientConfigurationDTO] = Field(
        None, description="MaleoMCU client's configuration"
    )

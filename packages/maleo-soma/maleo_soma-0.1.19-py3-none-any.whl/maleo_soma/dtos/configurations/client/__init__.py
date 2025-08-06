from pydantic import BaseModel, Field
from .maleo import MaleoClientsConfigurationDTO


DEFAULT_MALEO_CLIENTS_CONFIGURATIONS = MaleoClientsConfigurationDTO(
    telemetry=None,
    metadata=None,
    identity=None,
    access=None,
    workshop=None,
    soapie=None,
    medix=None,
    dicom=None,
    scribe=None,
    cds=None,
    imaging=None,
    mcu=None,
)


class ClientConfigurationDTO(BaseModel):
    maleo: MaleoClientsConfigurationDTO = Field(
        default=DEFAULT_MALEO_CLIENTS_CONFIGURATIONS,
        description="Maleo client's configurations",
    )

from sqlalchemy import Column, Enum
from maleo_soma.enums.status import DataStatus as DataStatusEnum


class DataStatus:
    status = Column(
        name="status",
        type_=Enum(enums=DataStatusEnum, name="statustype"),
        default=DataStatusEnum.ACTIVE,
        nullable=False,
    )

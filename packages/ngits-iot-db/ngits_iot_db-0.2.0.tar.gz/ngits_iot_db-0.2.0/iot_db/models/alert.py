from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON

from .base import AlertBase


class AlertDefinition(AlertBase):
    __tablename__ = "alert_definition"
    __table_args__ = (
        UniqueConstraint(
            "tenant",
            "meter_id",
        ),
    )

    properties = Column(JSON)

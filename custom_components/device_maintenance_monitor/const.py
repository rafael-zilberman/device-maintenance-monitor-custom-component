from enum import StrEnum
from typing import Final

DOMAIN: Final = "device_maintenance_monitor"
CONF_SENSOR_TYPE: Final = "sensor_type"
CONF_ENTITY_ID: Final = "entity_id"
CONF_COUNT: Final = "count"
CONF_INTERVAL: Final = "interval"
CONF_NAME: Final = "name"


class SensorType(StrEnum):
    """Possible modes for a maintenance monitoring."""

    RUNTIME = "runtime"
    COUNT = "count"
    FIXED_INTERVAL = "fixed_interval"

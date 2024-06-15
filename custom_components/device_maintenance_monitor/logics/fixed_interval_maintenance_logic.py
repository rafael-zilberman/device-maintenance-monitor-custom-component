from dataclasses import dataclass

from ..const import SensorType, CONF_INTERVAL, CONF_ENTITY_ID, CONF_NAME
from .base_maintenance_logic import MaintenanceData, MaintenanceLogic
from ..sensors import LastMaintenanceDateSensor


@dataclass
class FixedIntervalMaintenanceData(MaintenanceData):
    days_interval: int


class FixedIntervalMaintenanceLogic(MaintenanceLogic):
    sensor_type: SensorType = SensorType.FIXED_INTERVAL

    def _get_logic_data(self, data: dict) -> MaintenanceData:
        return FixedIntervalMaintenanceData(
            entity_id=data.get(CONF_ENTITY_ID),
            name=data.get(CONF_NAME),
            days_interval=data.get(CONF_INTERVAL),
        )

    def get_sensors(self):
        return [
            LastMaintenanceDateSensor(self),
        ]

    def is_maintenance_needed(self) -> bool:
        return True

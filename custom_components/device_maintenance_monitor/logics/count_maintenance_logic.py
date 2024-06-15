from dataclasses import dataclass

from ..const import SensorType, CONF_COUNT, CONF_ENTITY_ID, CONF_NAME
from .base_maintenance_logic import MaintenanceData, MaintenanceLogic
from ..sensors import LastMaintenanceDateSensor


@dataclass
class CountMaintenanceData(MaintenanceData):
    count: int


class CountMaintenanceLogic(MaintenanceLogic):
    sensor_type: SensorType = SensorType.COUNT

    def _get_logic_data(self, data: dict) -> MaintenanceData:
        return CountMaintenanceData(
            entity_id=data.get(CONF_ENTITY_ID),
            name=data.get(CONF_NAME),
            count=data.get(CONF_COUNT),
        )

    def get_sensors(self):
        return [
            LastMaintenanceDateSensor(self),
        ]

    def is_maintenance_needed(self) -> bool:
        return True

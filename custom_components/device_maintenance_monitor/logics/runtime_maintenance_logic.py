from dataclasses import dataclass

from ..const import SensorType, CONF_INTERVAL, CONF_ENTITY_ID, CONF_NAME
from .base_maintenance_logic import MaintenanceData, MaintenanceLogic
from ..sensors import LastMaintenanceDateSensor


@dataclass
class RuntimeMaintenanceData(MaintenanceData):
    hours_interval: int


class RuntimeMaintenanceLogic(MaintenanceLogic):
    sensor_type: SensorType = SensorType.RUNTIME

    def _get_logic_data(self, data: dict) -> MaintenanceData:
        return RuntimeMaintenanceData(
            entity_id=data.get(CONF_ENTITY_ID),
            name=data.get(CONF_NAME),
            hours_interval=data.get(CONF_INTERVAL),
        )

    def get_sensors(self):
        return [
            LastMaintenanceDateSensor(self),
        ]

    def is_maintenance_needed(self) -> bool:
        return True

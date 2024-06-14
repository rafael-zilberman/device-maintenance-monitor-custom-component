from dataclasses import dataclass

from custom_components.device_maintenance_monitor.const import SensorType, CONF_COUNT
from custom_components.device_maintenance_monitor.logics import MaintenanceData, MaintenanceLogic
from custom_components.device_maintenance_monitor.sensors import LastMaintenanceDateSensor


@dataclass
class CountMaintenanceData(MaintenanceData):
    count: int


class CountMaintenanceLogic(MaintenanceLogic):
    sensor_type: SensorType = SensorType.COUNT

    def _get_logic_data(self, data: dict) -> MaintenanceData:
        return CountMaintenanceData(
            entity_id=data.get("entity_id"),
            count=data.get(CONF_COUNT),
        )

    def get_sensors(self):
        return [
            LastMaintenanceDateSensor(self),
        ]

    def is_maintenance_needed(self) -> bool:
        return True

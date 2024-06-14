from dataclasses import dataclass

from custom_components.device_maintenance_monitor.const import SensorType, CONF_INTERVAL
from custom_components.device_maintenance_monitor.logics import MaintenanceData, MaintenanceLogic
from custom_components.device_maintenance_monitor.sensors import LastMaintenanceDateSensor


@dataclass
class RuntimeMaintenanceData(MaintenanceData):
    hours_interval: int


class RuntimeMaintenanceLogic(MaintenanceLogic):
    sensor_type: SensorType = SensorType.RUNTIME

    def _get_logic_data(self, data: dict) -> MaintenanceData:
        return RuntimeMaintenanceData(
            entity_id=data.get("entity_id"),
            hours_interval=data.get(CONF_INTERVAL),
        )

    def get_sensors(self):
        return [
            LastMaintenanceDateSensor(self),
        ]

    def is_maintenance_needed(self) -> bool:
        return True

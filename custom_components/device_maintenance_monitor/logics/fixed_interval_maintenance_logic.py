from dataclasses import dataclass

from custom_components.device_maintenance_monitor.const import SensorType, CONF_INTERVAL
from custom_components.device_maintenance_monitor.logics import MaintenanceData, MaintenanceLogic
from custom_components.device_maintenance_monitor.sensors import LastMaintenanceDateSensor


@dataclass
class FixedIntervalMaintenanceData(MaintenanceData):
    days_interval: int


class FixedIntervalMaintenanceLogic(MaintenanceLogic):
    sensor_type: SensorType = SensorType.FIXED_INTERVAL

    def _get_logic_data(self, data: dict) -> MaintenanceData:
        return FixedIntervalMaintenanceData(
            entity_id=data.get("entity_id"),
            days_interval=data.get(CONF_INTERVAL),
        )

    def get_sensors(self):
        return [
            LastMaintenanceDateSensor(self),
        ]

    def is_maintenance_needed(self) -> bool:
        return True

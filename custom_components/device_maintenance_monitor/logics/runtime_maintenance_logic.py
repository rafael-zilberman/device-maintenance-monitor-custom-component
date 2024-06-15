from dataclasses import dataclass

from ..const import SensorType, CONF_INTERVAL, CONF_ENTITY_ID, CONF_NAME, CONF_ON_STATES, DEFAULT_ON_STATES
from .base_maintenance_logic import MaintenanceData, MaintenanceLogic
from ..sensors import LastMaintenanceDateSensor, TotalRuntimeDurationSensor


@dataclass
class RuntimeMaintenanceData(MaintenanceData):
    hours_interval: int


class RuntimeMaintenanceLogic(MaintenanceLogic):
    sensor_type: SensorType = SensorType.RUNTIME

    def _get_logic_data(self, data: dict) -> MaintenanceData:
        return RuntimeMaintenanceData(
            entity_id=data.get(CONF_ENTITY_ID),
            name=data.get(CONF_NAME),
            on_states=data.get(CONF_ON_STATES) or DEFAULT_ON_STATES,
            hours_interval=data.get(CONF_INTERVAL),
        )

    def _get_sensors(self):
        return [
            LastMaintenanceDateSensor(self),
            TotalRuntimeDurationSensor(self),
        ]

    def is_maintenance_needed(self) -> bool:
        return True

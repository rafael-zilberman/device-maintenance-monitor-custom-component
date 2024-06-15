import logging
from dataclasses import dataclass
from datetime import timedelta

from ..const import SensorType, CONF_INTERVAL, CONF_ENTITY_ID, CONF_NAME, CONF_ON_STATES, DEFAULT_ON_STATES
from .base_maintenance_logic import MaintenanceData, MaintenanceLogic
from ..sensors import LastMaintenanceDateSensor, RuntimeDurationSensor
from homeassistant.helpers import config_validation as cv

_LOGGER = logging.getLogger(__name__)


@dataclass
class RuntimeMaintenanceData(MaintenanceData):
    interval: timedelta


class RuntimeMaintenanceLogic(MaintenanceLogic):
    sensor_type: SensorType = SensorType.RUNTIME

    def _get_logic_data(self, data: dict) -> MaintenanceData:
        return RuntimeMaintenanceData(
            entity_id=data.get(CONF_ENTITY_ID),
            name=data.get(CONF_NAME),
            on_states=data.get(CONF_ON_STATES) or DEFAULT_ON_STATES,
            interval=cv.time_period_dict(data.get(CONF_INTERVAL)),
        )

    def _get_sensors(self):
        return [
            LastMaintenanceDateSensor(self),
            RuntimeDurationSensor(self),
        ]

    @property
    def is_maintenance_needed(self) -> bool:
        return self.runtime_duration >= self._data.interval

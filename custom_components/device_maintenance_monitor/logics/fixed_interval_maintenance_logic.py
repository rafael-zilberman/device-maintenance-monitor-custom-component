from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import Optional

from ..const import SensorType, CONF_INTERVAL, CONF_ENTITY_ID, CONF_NAME, CONF_ON_STATES, DEFAULT_ON_STATES
from .base_maintenance_logic import MaintenanceData, MaintenanceLogic
from homeassistant.helpers import config_validation as cv


@dataclass
class FixedIntervalMaintenanceData(MaintenanceData):
    interval: timedelta


class FixedIntervalMaintenanceLogic(MaintenanceLogic):
    sensor_type: SensorType = SensorType.FIXED_INTERVAL

    def _get_logic_data(self, data: dict) -> MaintenanceData:
        return FixedIntervalMaintenanceData(
            entity_id=data.get(CONF_ENTITY_ID),
            name=data.get(CONF_NAME),
            on_states=data.get(CONF_ON_STATES) or DEFAULT_ON_STATES,
            interval=cv.time_period_dict(data.get(CONF_INTERVAL)),
        )

    @property
    def is_maintenance_needed(self) -> bool:
        if self._last_maintenance_date is None:
            return True
        return datetime.now() - self._last_maintenance_date >= self._data.interval

    @property
    def update_frequency(self) -> Optional[timedelta]:
        return timedelta(minutes=10)

    @property
    def predicted_maintenance_date(self) -> Optional[datetime]:
        if self._last_maintenance_date is None:
            return None
        return self._last_maintenance_date + self._data.interval

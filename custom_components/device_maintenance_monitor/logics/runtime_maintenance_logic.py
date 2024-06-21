import logging
from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import Dict, Optional

from ..const import SensorType, CONF_INTERVAL, CONF_ENTITY_ID, CONF_NAME, CONF_ON_STATES, DEFAULT_ON_STATES
from .base_maintenance_logic import MaintenanceData, MaintenanceLogic
from homeassistant.helpers import config_validation as cv

_LOGGER = logging.getLogger(__name__)


@dataclass
class RuntimeMaintenanceData(MaintenanceData):
    interval: timedelta


class RuntimeMaintenanceLogic(MaintenanceLogic):
    sensor_type: SensorType = SensorType.RUNTIME

    def _setup(self):
        self._last_device_on_time = None
        self._runtime_duration = timedelta(seconds=0)

    def _get_logic_data(self, data: dict) -> MaintenanceData:
        return RuntimeMaintenanceData(
            entity_id=data.get(CONF_ENTITY_ID),
            name=data.get(CONF_NAME),
            on_states=data.get(CONF_ON_STATES) or DEFAULT_ON_STATES,
            interval=cv.time_period_dict(data.get(CONF_INTERVAL)),
        )

    def _reset(self):
        # Reset the total runtime duration to 0
        self._runtime_duration = timedelta(seconds=0)

        if self._last_device_on_time:
            # If the device is on, reset the last device on time to the current time
            self._last_device_on_time = datetime.now()
        else:
            # Reset the last device on time to None
            self._last_device_on_time = None

    def _handle_turn_on(self):
        self._last_device_on_time = datetime.now()

    def _handle_turn_off(self):
        if self._last_device_on_time is None:
            return
        self._runtime_duration += (datetime.now() - self._last_device_on_time)
        self._last_device_on_time = None

    @property
    def is_maintenance_needed(self) -> bool:
        return self._runtime_duration >= self._data.interval

    def _get_state(self) -> Dict[str, str]:
        return {
            "runtime_duration": str(int(round(self._runtime_duration.total_seconds()))),
        }

    def _restore_state(self, state: Dict[str, str]):
        self._runtime_duration = timedelta(
            seconds=int(state.get("runtime_duration", self._runtime_duration.total_seconds())),
        )

    @property
    def update_frequency(self) -> Optional[timedelta]:
        return timedelta(minutes=1)

    @property
    def predicted_maintenance_date(self) -> Optional[datetime]:
        if self._last_maintenance_date is None:
            return None

        now = datetime.now()
        days_since_last_maintenance = (now - self._last_maintenance_date).total_seconds() / 86400
        if days_since_last_maintenance == 0:
            return None
        average_runtime_per_day = self._runtime_duration / days_since_last_maintenance
        if average_runtime_per_day == timedelta(seconds=0):
            return None
        runtime_left_until_maintenance = self._data.interval - self._runtime_duration
        days_left_until_maintenance = runtime_left_until_maintenance / average_runtime_per_day
        return now + timedelta(days=days_left_until_maintenance)

    def update(self):
        if self._last_device_on_time is None:
            return
        now = datetime.now()
        self._runtime_duration += (now - self._last_device_on_time)
        self._last_device_on_time = now

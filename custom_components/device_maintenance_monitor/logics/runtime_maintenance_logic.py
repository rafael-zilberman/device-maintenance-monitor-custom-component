"""The Device Maintenance Monitor integration."""
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from homeassistant.helpers import config_validation as cv

from ..const import (
    CONF_ENTITY_ID,
    CONF_INTERVAL,
    CONF_NAME,
    CONF_ON_STATES,
    DEFAULT_ON_STATES,
    DEFAULT_RUNTIME_UPDATE_FREQUENCY,
    STATE_RUNTIME_DURATION,
    SensorType,
)
from .base_maintenance_logic import MaintenanceData, MaintenanceLogic

_LOGGER = logging.getLogger(__name__)


@dataclass
class RuntimeMaintenanceData(MaintenanceData):
    """A data class that represents the runtime maintenance data of a device."""

    interval: timedelta


class RuntimeMaintenanceLogic(MaintenanceLogic):
    """A class that represents the logic for maintaining a device based on the runtime."""

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
        self._runtime_duration += datetime.now() - self._last_device_on_time
        self._last_device_on_time = None

    @property
    def is_maintenance_needed(self) -> bool:
        """Indicate whether maintenance is needed based on the runtime so far.

        :return: True if maintenance is needed, False otherwise.
        """
        return self._runtime_duration >= self._data.interval

    def _get_state(self) -> dict[str, str]:
        return {
            STATE_RUNTIME_DURATION: str(
                int(round(self._runtime_duration.total_seconds()))
            ),
        }

    def _restore_state(self, state: dict[str, str]):
        self._runtime_duration = timedelta(
            seconds=int(
                state.get(
                    STATE_RUNTIME_DURATION, self._runtime_duration.total_seconds()
                )
            ),
        )

    @property
    def update_frequency(self) -> timedelta | None:
        """Return the update frequency of the device.

        :return: The update frequency of the device.
        """
        return DEFAULT_RUNTIME_UPDATE_FREQUENCY

    @property
    def predicted_maintenance_date(self) -> datetime | None:
        """Return the predicted maintenance date based on the average runtime per day.

        :return: The predicted maintenance date.
        """
        if self._last_maintenance_date is None:
            return None

        # TODO: move to consts
        now = datetime.now()
        days_since_last_maintenance = (
            now - self._last_maintenance_date
        ).total_seconds() / 86400
        if days_since_last_maintenance == 0:
            return None
        average_runtime_per_day = self._runtime_duration / days_since_last_maintenance
        if average_runtime_per_day == timedelta(seconds=0):
            return None
        runtime_left_until_maintenance = self._data.interval - self._runtime_duration
        days_left_until_maintenance = (
            runtime_left_until_maintenance / average_runtime_per_day
        )
        return now + timedelta(days=days_left_until_maintenance)

    def update(self):
        """Update the runtime duration of the device."""
        if self._last_device_on_time is None:
            return
        now = datetime.now()
        self._runtime_duration += now - self._last_device_on_time
        self._last_device_on_time = now

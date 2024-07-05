"""A module that defines the logic for maintaining a device based on a fixed interval."""
from dataclasses import dataclass
from datetime import datetime, timedelta

from homeassistant.helpers import config_validation as cv

from ..const import (
    CONF_ENTITY_ID,
    CONF_INTERVAL,
    CONF_NAME,
    CONF_ON_STATES,
    DEFAULT_FIXED_INTERVAL_UPDATE_FREQUENCY,
    DEFAULT_ON_STATES,
    SensorType,
)
from .base_maintenance_logic import MaintenanceData, MaintenanceLogic


@dataclass
class FixedIntervalMaintenanceData(MaintenanceData):
    """A data class that represents the fixed interval maintenance data of a device."""

    interval: timedelta


class FixedIntervalMaintenanceLogic(MaintenanceLogic):
    """A class that represents the logic for maintaining a device based on a fixed interval."""

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
        """Indicate whether maintenance is needed based on the fixed interval.

        :return: True if maintenance is needed, False otherwise.
        """
        if self._last_maintenance_date is None:
            return True
        return datetime.now() - self._last_maintenance_date >= self._data.interval

    @property
    def update_frequency(self) -> timedelta | None:
        """Return the update frequency of the device.

        :return: The update frequency of the device.
        """
        return DEFAULT_FIXED_INTERVAL_UPDATE_FREQUENCY

    @property
    def predicted_maintenance_date(self) -> datetime | None:
        """Return the predicted maintenance date based on the fixed interval.

        :return: The predicted maintenance date.
        """
        if self._last_maintenance_date is None:
            return None
        return self._last_maintenance_date + self._data.interval

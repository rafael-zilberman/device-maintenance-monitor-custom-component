"""A module that defines the logic for maintaining a device based on a fixed interval."""
from datetime import datetime, timedelta

from ..const import (
    CONF_ENTITY_ID,
    CONF_INTERVAL,
    CONF_NAME,
    CONFIG_INITIAL_LAST_MAINTENANCE_DATE,
    DEFAULT_FIXED_INTERVAL_UPDATE_FREQUENCY,
)
from .base_maintenance_logic import MaintenanceLogic


class FixedIntervalMaintenanceLogic(MaintenanceLogic):
    """A class that represents the logic for maintaining a device based on a fixed interval."""

    _interval: timedelta  # The interval for maintenance

    def __init__(self, *,
                 name: str,
                 interval: timedelta,
                 entity_id: str | None,
                 initial_last_maintenance_date: datetime | None = None):
        """Initialize a new instance of the MaintenanceLogic class.

        :param name: The name of the entity.
        :param interval: The interval for maintenance.
        :param entity_id: The unique identifier of the source entity.
        :param initial_last_maintenance_date: The initial last maintenance date.
        """
        super().__init__(
            entity_id=entity_id,
            name=name,
            initial_last_maintenance_date=initial_last_maintenance_date,
        )
        self._interval = interval

    @classmethod
    def get_instance(cls, config: dict) -> "FixedIntervalMaintenanceLogic":
        """Return an instance of the maintenance logic.

        :param config: The configuration data of the device.
        :return: An instance of the maintenance logic.
        """
        return FixedIntervalMaintenanceLogic(
            name=config.get(CONF_NAME),
            interval=config.get(CONF_INTERVAL),
            entity_id=config.get(CONF_ENTITY_ID),
            initial_last_maintenance_date=config.get(CONFIG_INITIAL_LAST_MAINTENANCE_DATE),
        )

    @property
    def is_maintenance_needed(self) -> bool:
        """Indicate whether maintenance is needed based on the fixed interval.

        :return: True if maintenance is needed, False otherwise.
        """
        if self._last_maintenance_date is None:
            return True
        return datetime.now() - self._last_maintenance_date >= self._interval

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
        return self._last_maintenance_date + self._interval

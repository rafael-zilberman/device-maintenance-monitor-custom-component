"""A module that defines the logic for maintaining a device based on the turn on count."""
from datetime import datetime, timedelta
import logging

from ..const import (
    CONF_COUNT,
    CONF_ENTITY_ID,
    CONF_IS_ON_TEMPLATE,
    CONF_MAX_INTERVAL,
    CONF_MIN_INTERVAL,
    CONF_NAME,
    CONF_ON_STATES,
    DEFAULT_ON_STATES,
    STATE_DEVICE_TURN_ON_COUNT, CONFIG_INITIAL_LAST_MAINTENANCE_DATE, DATE_FORMAT,
)
from .base_maintenance_logic import IsOnExpression, MaintenanceLogic

_LOGGER = logging.getLogger(__name__)


class CountMaintenanceLogic(MaintenanceLogic):
    """A class that represents the logic for maintaining a device based on the turn on count."""

    _count: int  # The count of maintenance

    def __init__(self, *,
                 name: str,
                 count: int,
                 min_interval: timedelta | None,
                 max_interval: timedelta | None,
                 entity_id: str | None,
                 on_states: list[str] | None,
                 is_on_expression: IsOnExpression | None,
                 initial_last_maintenance_date: datetime | None = None):
        """Initialize a new instance of the MaintenanceLogic class.

        :param name: The name of the entity.
        :param count: The count of maintenance.
        :param min_interval: The minimum interval for maintenance.
        :param max_interval: The maximum interval for maintenance.
        :param entity_id: The unique identifier of the source entity.
        :param on_states: The states in which the device is considered to be "on".
        :param is_on_expression: The expression to determine if the device is on.
        :param initial_last_maintenance_date: The initial last maintenance date.
        """
        super().__init__(
            name=name,
            entity_id=entity_id,
            on_states=on_states,
            is_on_expression=is_on_expression,
            initial_last_maintenance_date=initial_last_maintenance_date,
        )
        self._count = count
        self._min_interval = min_interval
        self._max_interval = max_interval

        self._device_turn_on_count = 0

    @classmethod
    def get_instance(cls, config: dict) -> "CountMaintenanceLogic":
        """Return an instance of the maintenance logic.

        :param config: The configuration data of the device.
        :return: An instance of the maintenance logic.
        """
        return CountMaintenanceLogic(
            name=config.get(CONF_NAME),
            count=config.get(CONF_COUNT),
            min_interval=config.get(CONF_MIN_INTERVAL),
            max_interval=config.get(CONF_MAX_INTERVAL),
            entity_id=config.get(CONF_ENTITY_ID),
            on_states=config.get(CONF_ON_STATES) or DEFAULT_ON_STATES,
            is_on_expression=config.get(CONF_IS_ON_TEMPLATE),
            initial_last_maintenance_date=config.get(CONFIG_INITIAL_LAST_MAINTENANCE_DATE),
        )

    def _reset(self):
        self._device_turn_on_count = 0

    def _handle_turn_on(self):
        self._device_turn_on_count += 1

    @property
    def is_maintenance_needed(self) -> bool:
        """Indicate whether maintenance is needed based on the turn on count.

        :return: True if maintenance is needed, False otherwise.
        """
        # TODO: Create base class 'RangeMaintenanceLogic' and move this logic there (also from runtime logic)
        _LOGGER.info(
            "Checking if maintenance is needed for device '%s', Turn on count: %s, Min interval: %s, Max interval: "
            "%s, Count: %s, Last Maintenance Date: %s, Last Reset Date: %s",
            self._name,
            self._device_turn_on_count,
            self._min_interval,
            self._max_interval,
            self._count,
            self._last_maintenance_date,
            self._last_reset_date,
        )
        now = datetime.now()

        if self._max_interval:
            # Check if enough time has passed since the last maintenance
            max_maintenance_date = self._last_maintenance_date + self._max_interval
            if now > max_maintenance_date:
                return True

        if self._min_interval:
            # Check if the minimum interval has passed since the last maintenance
            min_maintenance_date = self._last_maintenance_date + self._min_interval
            if now < min_maintenance_date:
                return False

        # Check if the count has been reached
        return self._device_turn_on_count >= self._count

    def _get_state(self) -> dict[str, str]:
        return {
            STATE_DEVICE_TURN_ON_COUNT: str(self._device_turn_on_count),
        }

    def _restore_state(self, state: dict[str, str]):
        self._device_turn_on_count = int(
            state.get(STATE_DEVICE_TURN_ON_COUNT, self._device_turn_on_count)
        )

    @property
    def predicted_maintenance_date(self) -> datetime | None:
        """Return the predicted maintenance date based on the average turn on per day.

        :return: The predicted maintenance date.
        """
        if self._last_reset_date is None:
            return None

        now = datetime.now()
        days_since_last_maintenance = (
                                              now - self._last_reset_date
                                      ).total_seconds() / 86400
        if days_since_last_maintenance == 0:
            return None
        average_turn_on_per_day = (
                self._device_turn_on_count / days_since_last_maintenance
        )
        if average_turn_on_per_day == 0:
            return None
        turn_on_left_until_maintenance = self._count - self._device_turn_on_count
        days_left_until_maintenance = (
                turn_on_left_until_maintenance / average_turn_on_per_day
        )
        predicted_date = now + timedelta(days=days_left_until_maintenance)

        # TODO: Create base class 'RangeMaintenanceLogic' and move this logic there (also from runtime logic)
        # Ensure the predicted date falls within the min and max intervals
        if self._min_interval:
            min_maintenance_date = self._last_maintenance_date + self._min_interval
            if predicted_date < min_maintenance_date:
                return min_maintenance_date

        if self._max_interval:
            max_maintenance_date = self._last_maintenance_date + self._max_interval
            if predicted_date > max_maintenance_date:
                return max_maintenance_date

        return predicted_date

"""The Device Maintenance Monitor integration."""
from datetime import datetime, timedelta
import logging

from ..const import (
    CONF_ENTITY_ID,
    CONF_INTERVAL,
    CONF_IS_ON_TEMPLATE,
    CONF_MAX_INTERVAL,
    CONF_MIN_INTERVAL,
    CONF_NAME,
    CONF_ON_STATES,
    DEFAULT_ON_STATES,
    DEFAULT_RUNTIME_UPDATE_FREQUENCY,
    STATE_RUNTIME_DURATION,
)
from .base_maintenance_logic import IsOnExpression, MaintenanceLogic

_LOGGER = logging.getLogger(__name__)


class RuntimeMaintenanceLogic(MaintenanceLogic):
    """A class that represents the logic for maintaining a device based on the runtime."""

    _interval: timedelta  # The interval for maintenance
    _min_interval: timedelta | None  # The minimum interval for maintenance
    _max_interval: timedelta | None  # The maximum interval for maintenance

    def __init__(self, *,
                 name: str,
                 interval: timedelta,
                 min_interval: timedelta | None,
                 max_interval: timedelta | None,
                 entity_id: str | None,
                 on_states: list[str] | None,
                 is_on_expression: IsOnExpression | None):
        """Initialize a new instance of the MaintenanceLogic class.

        :param name: The name of the entity.
        :param interval: The interval for maintenance.
        :param min_interval: The minimum interval for maintenance.
        :param max_interval: The maximum interval for maintenance.
        :param entity_id: The unique identifier of the source entity.
        :param on_states: The states in which the device is considered to be "on".
        :param is_on_expression: The expression to determine if the device is on.
        """
        super().__init__(
            name=name,
            entity_id=entity_id,
            on_states=on_states,
            is_on_expression=is_on_expression,
        )
        self._interval = interval
        self._min_interval = min_interval
        self._max_interval = max_interval

        self._last_device_on_time = None
        self._runtime_duration = timedelta(seconds=0)

    @classmethod
    def get_instance(cls, config: dict) -> "RuntimeMaintenanceLogic":
        """Return an instance of the maintenance logic.

        :param config: The configuration data of the device.
        :return: An instance of the maintenance logic.
        """
        return RuntimeMaintenanceLogic(
            name=config.get(CONF_NAME),
            interval=config.get(CONF_INTERVAL),
            min_interval=config.get(CONF_MIN_INTERVAL),
            max_interval=config.get(CONF_MAX_INTERVAL),
            entity_id=config.get(CONF_ENTITY_ID),
            on_states=config.get(CONF_ON_STATES) or DEFAULT_ON_STATES,
            is_on_expression=config.get(CONF_IS_ON_TEMPLATE),
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
        _LOGGER.info(
            "Checking if maintenance is needed for device '%s', Runtime duration: %s, Min interval: %s, Max interval: "
            "%s, Interval: %s, Last Maintenance Date: %s",
            self._name,
            self._runtime_duration,
            self._min_interval,
            self._max_interval,
            self._interval,
            self._last_maintenance_date,
        )
        now = datetime.now()
        if self._max_interval:
            max_maintenance_date = self._last_maintenance_date + self._max_interval
            return now > max_maintenance_date

        if self._min_interval and self._runtime_duration >= self._min_interval:
            min_maintenance_date = self._last_maintenance_date + self._min_interval
            return now > min_maintenance_date and self._runtime_duration >= self._interval

        return self._runtime_duration >= self._interval

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
        days_since_last_maintenance = (now - self._last_maintenance_date).total_seconds() / 86400
        if days_since_last_maintenance == 0:
            return None

        average_runtime_per_day = self._runtime_duration / days_since_last_maintenance
        if not average_runtime_per_day:
            # Avoid division by zero
            return None

        runtime_left_until_maintenance = self._interval - self._runtime_duration

        days_left_until_maintenance = runtime_left_until_maintenance / average_runtime_per_day

        predicted_date = now + timedelta(days=days_left_until_maintenance)

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

    def update(self):
        """Update the runtime duration of the device."""
        if self._last_device_on_time is None:
            return
        now = datetime.now()
        self._runtime_duration += now - self._last_device_on_time
        self._last_device_on_time = now

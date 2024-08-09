"""A module that defines the logic for maintaining a device based on the turn on count."""
from datetime import datetime, timedelta

from ..const import (
    CONF_COUNT,
    CONF_ENTITY_ID,
    CONF_IS_ON_TEMPLATE,
    CONF_NAME,
    CONF_ON_STATES,
    DEFAULT_ON_STATES,
    STATE_DEVICE_TURN_ON_COUNT,
)
from .base_maintenance_logic import IsOnExpression, MaintenanceLogic


class CountMaintenanceLogic(MaintenanceLogic):
    """A class that represents the logic for maintaining a device based on the turn on count."""

    _count: int  # The count of maintenance

    def __init__(self, *,
                 name: str,
                 count: int,
                 entity_id: str | None,
                 on_states: list[str] | None,
                 is_on_expression: IsOnExpression | None):
        """Initialize a new instance of the MaintenanceLogic class.

        :param name: The name of the entity.
        :param count: The count of maintenance.
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
        self._count = count
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
            entity_id=config.get(CONF_ENTITY_ID),
            on_states=config.get(CONF_ON_STATES) or DEFAULT_ON_STATES,
            is_on_expression=config.get(CONF_IS_ON_TEMPLATE),
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
        if self._last_maintenance_date is None:
            return None
        now = datetime.now()
        days_since_last_maintenance = (
                                              now - self._last_maintenance_date
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
        return now + timedelta(days=days_left_until_maintenance)

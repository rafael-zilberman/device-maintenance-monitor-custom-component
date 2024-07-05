"""A module that defines the logic for maintaining a device based on the turn on count."""
from dataclasses import dataclass
from datetime import datetime, timedelta

from ..const import (
    CONF_COUNT,
    CONF_ENTITY_ID,
    CONF_NAME,
    CONF_ON_STATES,
    DEFAULT_ON_STATES,
    STATE_DEVICE_TURN_ON_COUNT,
    SensorType,
)
from .base_maintenance_logic import MaintenanceData, MaintenanceLogic


@dataclass
class CountMaintenanceData(MaintenanceData):
    """A data class that represents the count maintenance data of a device."""

    count: int  # The count of maintenance


class CountMaintenanceLogic(MaintenanceLogic):
    """A class that represents the logic for maintaining a device based on the turn on count."""

    sensor_type: SensorType = SensorType.COUNT

    def _setup(self):
        self._device_turn_on_count = 0

    def _get_logic_data(self, data: dict) -> MaintenanceData:
        return CountMaintenanceData(
            entity_id=data.get(CONF_ENTITY_ID),
            name=data.get(CONF_NAME),
            on_states=data.get(CONF_ON_STATES) or DEFAULT_ON_STATES,
            count=data.get(CONF_COUNT),
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
        return self._device_turn_on_count >= self._data.count

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
        turn_on_left_until_maintenance = self._data.count - self._device_turn_on_count
        days_left_until_maintenance = (
                turn_on_left_until_maintenance / average_turn_on_per_day
        )
        return now + timedelta(days=days_left_until_maintenance)

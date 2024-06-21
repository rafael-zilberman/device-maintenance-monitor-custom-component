from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional

from ..const import SensorType, CONF_COUNT, CONF_ENTITY_ID, CONF_NAME, CONF_ON_STATES, DEFAULT_ON_STATES
from .base_maintenance_logic import MaintenanceData, MaintenanceLogic


@dataclass
class CountMaintenanceData(MaintenanceData):
    count: int


class CountMaintenanceLogic(MaintenanceLogic):
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
        # Reset the device turn on count to 0
        self._device_turn_on_count = 0

    def _handle_turn_on(self):
        self._device_turn_on_count += 1

    @property
    def is_maintenance_needed(self) -> bool:
        return self._device_turn_on_count >= self._data.count

    def _get_state(self) -> Dict[str, str]:
        return {
            "device_turn_on_count": str(self._device_turn_on_count),
        }

    def _restore_state(self, state: Dict[str, str]):
        self._device_turn_on_count = int(state.get("device_turn_on_count", self._device_turn_on_count))

    @property
    def predicted_maintenance_date(self) -> Optional[datetime]:
        if self._last_maintenance_date is None:
            return None
        # TODO: move to consts
        now = datetime.now()
        days_since_last_maintenance = (now - self._last_maintenance_date).total_seconds() / 86400
        if days_since_last_maintenance == 0:
            return None
        average_turn_on_per_day = self._device_turn_on_count / days_since_last_maintenance
        if average_turn_on_per_day == 0:
            return None
        turn_on_left_until_maintenance = self._data.count - self._device_turn_on_count
        days_left_until_maintenance = turn_on_left_until_maintenance / average_turn_on_per_day
        return now + timedelta(days=days_left_until_maintenance)

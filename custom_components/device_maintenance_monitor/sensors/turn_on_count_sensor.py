import logging
from datetime import timedelta
from typing import Optional

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import UnitOfTime

from .base_maintenance_sensor import MaintenanceSensor

_LOGGER = logging.getLogger(__name__)


class TurnOnCountSensor(MaintenanceSensor):
    key: str = "turn_on_count"

    @property
    def state(self) -> Optional[str]:
        return str(self.logic.device_turn_on_count)

    def restore_state(self, state: str):
        self.logic.set_device_turn_on_count(int(state))

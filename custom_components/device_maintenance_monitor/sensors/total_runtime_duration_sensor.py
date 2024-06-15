import logging
from typing import Optional

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import UnitOfTime

from .base_maintenance_sensor import MaintenanceSensor

_LOGGER = logging.getLogger(__name__)


class TotalRuntimeDurationSensor(MaintenanceSensor[int]):
    key: str = "total_runtime_duration"

    @property
    def device_class(self) -> SensorDeviceClass:
        return SensorDeviceClass.DURATION

    @property
    def unit_of_measurement(self) -> Optional[str]:
        return UnitOfTime.SECONDS

    @property
    def state(self) -> Optional[int]:
        return self.logic.total_runtime_duration

    def restore_state(self, state: int):
        self.logic.set_total_runtime_duration(state)

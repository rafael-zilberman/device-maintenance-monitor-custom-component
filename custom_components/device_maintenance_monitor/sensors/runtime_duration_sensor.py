import logging
from datetime import timedelta
from typing import Optional

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import UnitOfTime

from .base_maintenance_sensor import MaintenanceSensor

_LOGGER = logging.getLogger(__name__)


class RuntimeDurationSensor(MaintenanceSensor):
    key: str = "runtime_duration"

    @property
    def device_class(self) -> Optional[SensorDeviceClass]:
        return SensorDeviceClass.DURATION

    @property
    def unit_of_measurement(self) -> Optional[str]:
        return UnitOfTime.SECONDS

    @property
    def state(self) -> Optional[str]:
        return str(int(self.logic.runtime_duration.total_seconds()))

    def restore_state(self, state: str):
        self.logic.set_runtime_duration(timedelta(seconds=int(state)))

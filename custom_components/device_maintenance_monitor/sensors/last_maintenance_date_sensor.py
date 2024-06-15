import logging
from datetime import datetime
from typing import Optional

from homeassistant.components.sensor import SensorDeviceClass

from .base_maintenance_sensor import MaintenanceSensor

_LOGGER = logging.getLogger(__name__)


class LastMaintenanceDateSensor(MaintenanceSensor[str]):
    key: str = "last_maintenance_date"

    @property
    def device_class(self) -> SensorDeviceClass:
        return SensorDeviceClass.TIMESTAMP

    @property
    def state(self) -> Optional[str]:
        return self.logic.last_maintenance_date.strftime('%Y-%m-%d %H:%M:%S')

    def restore_state(self, state: str):
        self.logic.set_last_maintenance_date(datetime.strptime(state, '%Y-%m-%d %H:%M:%S'))

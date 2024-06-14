import logging

from .base_maintenance_sensor import MaintenanceSensor
from ..logics.base_maintenance_logic import MaintenanceLogic

_LOGGER = logging.getLogger(__name__)


class LastMaintenanceDateSensor(MaintenanceSensor):
    key: str = "last_maintenance_date"

from typing import List, Type

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from ..const import CONF_SENSOR_TYPE
from .base_maintenance_logic import MaintenanceData, MaintenanceLogic
from .fixed_interval_maintenance_logic import FixedIntervalMaintenanceLogic
from .count_maintenance_logic import CountMaintenanceLogic
from .runtime_maintenance_logic import RuntimeMaintenanceLogic

IMPLEMENTED_LOGICS: List[Type[MaintenanceLogic]] = [
    RuntimeMaintenanceLogic,
    CountMaintenanceLogic,
    FixedIntervalMaintenanceLogic,
]


def get_maintenance_logic(hass: HomeAssistant, config_entry: ConfigEntry) -> MaintenanceData:
    sensor_type = config_entry.data.get(CONF_SENSOR_TYPE)
    if not sensor_type:
        raise ValueError(f"sensor_type is required in {config_entry.data}")

    logic_type_by_sensor_type = {
        logic.sensor_type: logic for logic in IMPLEMENTED_LOGICS
    }

    sensor_logic = logic_type_by_sensor_type.get(sensor_type)
    if not sensor_logic:
        raise NotImplementedError(f"sensor_type {sensor_type} is not implemented")

    return sensor_logic(hass, config_entry)

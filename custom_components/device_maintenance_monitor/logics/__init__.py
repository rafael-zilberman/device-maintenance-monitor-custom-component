from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from ..common import create_source_entity
from ..const import CONF_ENTITY_ID, CONF_SENSOR_TYPE
from .base_maintenance_logic import MaintenanceLogic
from .count_maintenance_logic import CountMaintenanceLogic
from .fixed_interval_maintenance_logic import FixedIntervalMaintenanceLogic
from .runtime_maintenance_logic import RuntimeMaintenanceLogic

IMPLEMENTED_LOGICS: list[type[MaintenanceLogic]] = [
    RuntimeMaintenanceLogic,
    CountMaintenanceLogic,
    FixedIntervalMaintenanceLogic,
]


async def get_maintenance_logic(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> MaintenanceLogic:
    sensor_type = config_entry.data.get(CONF_SENSOR_TYPE)
    if sensor_type is None:
        raise ValueError(f"{CONF_SENSOR_TYPE} is required in {config_entry.data}")

    source_entity_id = config_entry.data.get(CONF_ENTITY_ID)
    if source_entity_id is None:
        raise ValueError(f"{CONF_ENTITY_ID} is required in {config_entry.data}")

    logic_type_by_sensor_type = {
        logic.sensor_type: logic for logic in IMPLEMENTED_LOGICS
    }

    sensor_logic = logic_type_by_sensor_type.get(sensor_type)
    if sensor_logic is None:
        raise NotImplementedError(f"sensor_type {sensor_type} is not implemented")

    source_entity = await create_source_entity(
        source_entity_id,
        hass,
    )
    config_data = dict(config_entry.data)
    return sensor_logic(
        config_data=config_data,
        source_entity=source_entity,
    )

import logging
from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import StateType

from .const import CONF_ENTITY_ID, DOMAIN
from .device_binding import bind_config_entry_to_device
from .logics import MaintenanceLogic
from .sensors import MaintenanceSensor

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    _LOGGER.info(f"Setting up entry {entry.entry_id} (sensors)")
    bind_config_entry_to_device(hass, entry)

    logic: MaintenanceLogic = hass.data[DOMAIN][entry.entry_id]
    entities_to_add = [
        MaintenanceSensorEntity(sensor)
        for sensor in logic.get_sensors()
    ]
    _LOGGER.info(f"Adding entities ({len(entities_to_add)}): {entities_to_add}")
    async_add_entities(entities_to_add)


@dataclass(frozen=True, kw_only=True)
class MaintenanceSensorEntityDescription(SensorEntityDescription):
    """Class describing sensors entities."""


class MaintenanceSensorEntity(SensorEntity, RestoreEntity):
    def __init__(self, sensor: MaintenanceSensor):
        self.entity_description = MaintenanceSensorEntityDescription(
            key=sensor.key,
            has_entity_name=True,
            translation_key=sensor.key,
        )
        self._attr_unique_id = f"{sensor.source_entity_id}_{sensor.key}"

    @property
    def native_value(self) -> StateType:
        return "Hello"

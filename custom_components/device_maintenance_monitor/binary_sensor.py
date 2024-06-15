import logging
from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.core import HomeAssistant

from .device_binding import get_device_info
from .const import DOMAIN
from .logics import MaintenanceLogic

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    _LOGGER.info(f"Setting up entry {entry.entry_id} (binary sensors)")
    logic: MaintenanceLogic = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        MaintenanceNeededBinarySensorEntity(logic)
    ])


@dataclass(frozen=True, kw_only=True)
class MaintenanceBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing binary sensors entities."""


class MaintenanceNeededBinarySensorEntity(BinarySensorEntity):
    def __init__(self, logic: MaintenanceLogic):
        self._logic = logic
        self.entity_description = MaintenanceBinarySensorEntityDescription(
            key="maintenance_needed",
            has_entity_name=True,
            translation_key="maintenance_needed",
        )
        self._attr_unique_id = f"{logic.source_entity.entity_id}_maintenance_needed"
        self._attr_device_info = get_device_info(logic.source_entity)

    @property
    def is_on(self):
        return self._logic.is_maintenance_needed

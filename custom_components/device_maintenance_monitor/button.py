import logging
from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant

from .device_binding import get_device_info
from .const import DOMAIN
from .logics import MaintenanceLogic

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    _LOGGER.info(f"Setting up entry {entry.entry_id} (button)")
    logic: MaintenanceLogic = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        ResetMaintenanceButtonEntity(logic)
    ])


@dataclass(frozen=True, kw_only=True)
class MaintenanceButtonEntityDescription(ButtonEntityDescription):
    """Class describing button entities."""


class ResetMaintenanceButtonEntity(ButtonEntity):
    def __init__(self, logic: MaintenanceLogic):
        self._logic = logic
        self.entity_description = MaintenanceButtonEntityDescription(
            key="reset_maintenance",
            has_entity_name=True,
            translation_key="reset_maintenance",
        )
        self._attr_unique_id = f"{logic.source_entity.entity_id}_reset_maintenance"
        self._attr_device_info = get_device_info(logic.source_entity)

    async def async_press(self):
        # Reset the device maintenance monitor metrics
        pass

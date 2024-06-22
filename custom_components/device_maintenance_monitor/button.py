from dataclasses import dataclass
import logging

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    DOMAIN,
    ENTITY_BUTTON_KEY,
    ENTITY_BUTTON_TRANSLATION_KEY,
    SIGNAL_SENSOR_STATE_CHANGE,
)
from .device_binding import get_device_info
from .logics import MaintenanceLogic

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up the button platform."""
    logic: MaintenanceLogic = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ResetMaintenanceButtonEntity(logic)])


@dataclass(frozen=True, kw_only=True)
class MaintenanceButtonEntityDescription(ButtonEntityDescription):
    """Class describing button entities."""


class ResetMaintenanceButtonEntity(ButtonEntity):
    """A class that represents a button entity for resetting the maintenance monitor metrics."""

    def __init__(self, logic: MaintenanceLogic):
        """Initialize the button entity.

        :param logic: The maintenance logic to be used.
        """
        self.entity_description = MaintenanceButtonEntityDescription(
            key=ENTITY_BUTTON_KEY,
            has_entity_name=True,
            translation_key=ENTITY_BUTTON_TRANSLATION_KEY,
        )
        self._attr_unique_id = f"{logic.source_entity.entity_id}_reset_maintenance"
        self._attr_device_info = get_device_info(logic.source_entity)

        self._logic = logic

    async def async_press(self) -> None:
        """Handle the press of the button."""
        # Reset the device maintenance monitor metrics
        self._logic.reset()

        # Update the state of the button
        self.async_write_ha_state()

        # Notify the sensor to update its state
        async_dispatcher_send(self.hass, SIGNAL_SENSOR_STATE_CHANGE)

from typing import List

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, Event
from homeassistant.helpers.event import async_track_state_change_event

from .device_binding import bind_config_entry_to_device
from .const import DOMAIN
from .logics import get_maintenance_logic

PLATFORMS: List[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a config entry."""
    logic = await get_maintenance_logic(hass, entry)

    # Bind the config entry to the device from the source entity if it is not already bound
    bind_config_entry_to_device(hass, entry, logic.source_entity)

    # Set up sensors, binary sensors, and buttons
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = logic
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    def handle_state_change(event: Event):
        old_state = event.data.get('old_state')
        new_state = event.data.get('new_state')

        if old_state is not None:
            old_state_value = old_state.state
        else:
            old_state_value = None

        if new_state is not None:
            new_state_value = new_state.state
        else:
            new_state_value = None
        logic.handle_source_entity_state_change(old_state_value, new_state_value)

    async_track_state_change_event(hass, logic.source_entity.entity_id, handle_state_change)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return True

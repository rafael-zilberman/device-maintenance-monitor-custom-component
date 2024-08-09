"""The Device Maintenance Monitor integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .common import create_source_entity
from .const import DOMAIN
from .device_binding import bind_config_entry_to_device
from .logics import get_maintenance_logic

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a config entry."""

    # Get the maintenance logic for the entry
    logic = await get_maintenance_logic(hass, entry)

    # Bind the config entry to the device from the source entity if it is not already bound
    source_entity = None
    if logic.source_entity_id:
        source_entity = await create_source_entity(logic.source_entity_id, hass)
        bind_config_entry_to_device(hass, entry, source_entity)

    # Set up sensors, binary sensors, and buttons
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = logic
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

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

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN


async def async_setup(hass: HomeAssistant, config: dict):
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Set up sensors, binary sensors, and buttons
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, 'sensor')
    )
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, 'binary_sensor')
    )
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, 'button')
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    # Unload sensors, binary sensors, and buttons
    await hass.config_entries.async_forward_entry_unload(entry, 'sensor')
    await hass.config_entries.async_forward_entry_unload(entry, 'binary_sensor')
    await hass.config_entries.async_forward_entry_unload(entry, 'button')

    hass.data[DOMAIN].pop(entry.entry_id)

    return True

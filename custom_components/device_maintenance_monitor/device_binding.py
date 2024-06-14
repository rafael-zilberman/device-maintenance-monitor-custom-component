import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry

_LOGGER = logging.getLogger(__name__)


def bind_config_entry_to_device(
        hass: HomeAssistant,
        config_entry: ConfigEntry
) -> None:
    """
    When the user selected a specific device in the config flow, bind the config entry to that device
    This will let HA bind all the entities for that config entry to the concerning device
    """
    device_id = config_entry.data.get(CONF_DEVICE)
    if not device_id:
        return

    device_reg = device_registry.async_get(hass)
    device_entry = device_reg.async_get(device_id)
    if device_entry and config_entry.entry_id not in device_entry.config_entries:
        device_reg.async_update_device(
            device_id,
            add_config_entry_id=config_entry.entry_id,
        )

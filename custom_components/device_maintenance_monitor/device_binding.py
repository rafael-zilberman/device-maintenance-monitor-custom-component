"""Helper functions for binding devices to config entries."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo

from .common import SourceEntity

_LOGGER = logging.getLogger(__name__)


def bind_config_entry_to_device(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    source_entity: SourceEntity,
) -> None:
    """Bind the config entry to the device from the source entity if it is not already bound."""
    device_entry = source_entity.device_entry
    device_reg = dr.async_get(hass)
    if device_entry and config_entry.entry_id not in device_entry.config_entries:
        device_reg.async_update_device(
            device_entry.id,
            add_config_entry_id=config_entry.entry_id,
        )


def get_device_info(source_entity: SourceEntity) -> DeviceInfo | None:
    """Get the device info for the source entity."""
    device = source_entity.device_entry

    if device is None:
        return None

    if not device.identifiers and not device.connections:
        return None

    return DeviceInfo(
        identifiers=device.identifiers,
        connections=device.connections,
    )

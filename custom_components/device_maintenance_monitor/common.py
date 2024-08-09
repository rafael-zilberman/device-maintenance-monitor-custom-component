"""Common functions for the device maintenance monitor integration."""
import logging
from typing import NamedTuple

from homeassistant.components.light import ATTR_SUPPORTED_COLOR_MODES, ColorMode
from homeassistant.core import HomeAssistant, callback, split_entity_id
import homeassistant.helpers.device_registry as dr
from homeassistant.helpers.entity import async_generate_entity_id
import homeassistant.helpers.entity_registry as er

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SourceEntity(NamedTuple):
    """A class that represents the source entity of the device."""

    object_id: str
    entity_id: str
    domain: str
    unique_id: str | None = None
    name: str | None = None
    supported_color_modes: list[ColorMode] | None = None
    entity_entry: er.RegistryEntry | None = None
    device_entry: dr.DeviceEntry | None = None


async def create_source_entity(entity_id: str, hass: HomeAssistant) -> SourceEntity:
    """Create object containing all information about the source entity."""

    source_entity_domain, source_object_id = split_entity_id(entity_id)
    entity_registry = er.async_get(hass)
    entity_entry = entity_registry.async_get(entity_id)

    device_registry = dr.async_get(hass)
    device_entry = (
        device_registry.async_get(entity_entry.device_id)
        if entity_entry and entity_entry.device_id
        else None
    )

    unique_id = None
    supported_color_modes: list[ColorMode] = []
    if entity_entry:
        source_entity_domain = entity_entry.domain
        unique_id = entity_entry.unique_id
        if entity_entry.capabilities:
            supported_color_modes = entity_entry.capabilities.get(  # type: ignore[assignment]
                ATTR_SUPPORTED_COLOR_MODES,
            )

    entity_state = hass.states.get(entity_id)
    if entity_state:
        supported_color_modes = entity_state.attributes.get(ATTR_SUPPORTED_COLOR_MODES)

    return SourceEntity(
        source_object_id,
        entity_id,
        source_entity_domain,
        unique_id,
        get_wrapped_entity_name(
            hass,
            entity_id,
            source_object_id,
            entity_entry,
            device_entry,
        ),
        supported_color_modes or [],
        entity_entry,
        device_entry,
    )


def get_wrapped_entity_name(
        hass: HomeAssistant,
        entity_id: str,
        object_id: str,
        entity_entry: er.RegistryEntry | None,
        device_entry: dr.DeviceEntry | None,
) -> str:
    """Construct entity name based on the wrapped entity."""
    if entity_entry:
        if entity_entry.name is None and entity_entry.has_entity_name and device_entry:
            return device_entry.name_by_user or device_entry.name or object_id

        return entity_entry.name or entity_entry.original_name or object_id

    entity_state = hass.states.get(entity_id)
    if entity_state:
        return str(entity_state.name)

    return object_id


def get_entity_id_by_unique_id(
        hass: HomeAssistant,
        sensor_domain: str,
        unique_id: str,
) -> str | None:
    """Get the entity_id based on the unique_id.

    :param hass: The Home Assistant instance.
    :param sensor_domain: The domain of the sensor.
    :param unique_id: The unique identifier of the entity.
    :return: The entity_id of the entity.
    """
    entity_reg = er.async_get(hass)
    return entity_reg.async_get_entity_id(sensor_domain, DOMAIN, unique_id)


@callback
def generate_sensor_entity_id(
        hass: HomeAssistant,
        sensor_domain: str,
        suffix: str,
        source_entity: SourceEntity | None = None,
        name: str | None = None,
        unique_id: str | None = None,
) -> str:
    """Generate the entity_id to use for a sensor.

    :param hass: The Home Assistant instance.
    :param sensor_domain: The domain of the sensor.
    :param suffix: The suffix of the sensor.
    :param source_entity: The source entity of the sensor.
    :param name: The name of the sensor.
    :param unique_id: The unique identifier of the sensor.
    :return: The entity_id of the sensor.
    """
    if entity_id := get_entity_id_by_unique_id(hass, sensor_domain, unique_id):
        return entity_id
    if source_entity:
        object_id = source_entity.object_id
    else:
        object_id = name
    return async_generate_entity_id(
        sensor_domain + ".{}",
        f"{object_id}_{suffix}",
        hass=hass,
    )

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
from .device_binding import get_device_info
from .logics import MaintenanceLogic
from .sensors import MaintenanceSensor

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    _LOGGER.info(f"Setting up entry {entry.entry_id} (sensors)")

    logic: MaintenanceLogic = hass.data[DOMAIN][entry.entry_id]
    entities_to_add = [
        MaintenanceSensorEntity(sensor)
        for sensor in logic.sensors
    ]
    _LOGGER.info(f"Adding entities ({len(entities_to_add)}): {entities_to_add}")
    async_add_entities(entities_to_add)


@dataclass(frozen=True, kw_only=True)
class MaintenanceSensorEntityDescription(SensorEntityDescription):
    """Class describing sensors entities."""


class MaintenanceSensorEntity(SensorEntity, RestoreEntity):
    def __init__(self, sensor: MaintenanceSensor):
        self.entity_description = MaintenanceSensorEntityDescription(
            device_class=sensor.device_class,
            native_unit_of_measurement=sensor.unit_of_measurement,
            key=sensor.key,
            has_entity_name=True,
            translation_key=sensor.key,
        )
        self._attr_unique_id = sensor.id
        self._attr_device_info = get_device_info(sensor.source_entity)

        self._sensor = sensor

    @property
    def state(self):
        return self._sensor.state

    async def async_added_to_hass(self):
        last_state = await self.async_get_last_state()
        if last_state:
            self._sensor.restore_state(last_state.state)

    def update(self):
        pass

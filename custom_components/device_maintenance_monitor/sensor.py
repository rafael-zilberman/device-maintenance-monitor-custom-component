"""The sensors for the Device Maintenance Monitor integration."""
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.typing import StateType

from .common import SourceEntity, create_source_entity, generate_sensor_entity_id
from .const import DOMAIN, SIGNAL_SENSOR_STATE_CHANGE, STATE_PREDICTED_MAINTENANCE_DATE
from .device_binding import get_device_info
from .logics import MaintenanceLogic

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class MaintenanceSensorEntityDescription(SensorEntityDescription):
    """Class describing sensors entities."""

    value_fn: Callable[[MaintenanceLogic], str | float | datetime]


class MaintenanceDurationSensorEntity(SensorEntity):
    """A class that represents a sensor entity for indicating how long the device has been running."""

    entity_description: MaintenanceSensorEntityDescription

    def __init__(self,
                 hass: HomeAssistant,
                 logic: MaintenanceLogic,
                 unique_id: str,
                 source_entity: SourceEntity | None,
                 description: MaintenanceSensorEntityDescription):
        """Initialize the sensor entity.

        :param logic: The maintenance logic to be  used.
        """
        self.entity_description = description
        self._attr_unique_id = f"{unique_id}_{description.key}"
        self._attr_translation_key = f"{description.key}"

        if source_entity:
            self._attr_device_info = get_device_info(source_entity)
        self.entity_id = generate_sensor_entity_id(
            hass,
            "sensor",
            description.key,
            source_entity,
            logic.name,
            self.unique_id,
        )

        self._logic = logic

    @property
    def native_value(self) -> StateType:
        """Return the state."""
        return self.entity_description.value_fn(self._logic)

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        @callback
        def signal_sensor_state_change_listener() -> None:
            self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_SENSOR_STATE_CHANGE,
                signal_sensor_state_change_listener,
            )
        )


MAINTENANCE_SENSORS: list[MaintenanceSensorEntityDescription] = [
    MaintenanceSensorEntityDescription(
        key=STATE_PREDICTED_MAINTENANCE_DATE,
        device_class=SensorDeviceClass.DATE,
        value_fn=lambda logic: logic.predicted_maintenance_date,
    ),
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the sensor platform."""

    logic: MaintenanceLogic = hass.data[DOMAIN][entry.entry_id]
    source_entity = None
    if logic.source_entity_id:
        source_entity = await create_source_entity(logic.source_entity_id, hass)
    _LOGGER.info(
        "Setting up sensor entities for entry '%s' of device '%s' using %s logic type",
        entry,
        logic.source_entity_id,
        logic.logic_type
    )
    async_add_entities([
        MaintenanceDurationSensorEntity(hass, logic, entry.unique_id, source_entity, sensor_description)
        for sensor_description in MAINTENANCE_SENSORS
    ])

"""The sensors for the Device Maintenance Monitor integration."""
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant, callback, split_entity_id
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.typing import StateType

from .const import (
    DOMAIN,
    SIGNAL_SENSOR_STATE_CHANGE,
    STATE_DEVICE_TURN_ON_COUNT,
    STATE_PREDICTED_MAINTENANCE_DATE,
    STATE_RUNTIME_DURATION,
    SensorType,
)
from .device_binding import get_device_info
from .logics import MaintenanceLogic

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class MaintenanceSensorEntityDescription(SensorEntityDescription):
    """Class describing sensors entities."""

    sensor_types: list[SensorType]
    value_fn: Callable[[MaintenanceLogic], str | float | datetime]


class MaintenanceDurationSensorEntity(SensorEntity):
    """A class that represents a sensor entity for indicating how long the device has been running."""

    entity_description: MaintenanceSensorEntityDescription

    def __init__(self, logic: MaintenanceLogic, unique_id: str, description: MaintenanceSensorEntityDescription):
        """Initialize the sensor entity.

        :param logic: The maintenance logic to be  used.
        """
        self.entity_description = description
        self._attr_unique_id = f"{unique_id}_{description.key}"
        self._attr_translation_key = f"{description.key}"
        self._attr_device_info = get_device_info(logic.source_entity)

        object_id = split_entity_id(logic.source_entity.entity_id)[1]
        self.entity_id = f"sensor.{object_id}_{description.key}"

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
        sensor_types=SensorType.all_types(),
        value_fn=lambda logic: logic.predicted_maintenance_date,
    ),
    MaintenanceSensorEntityDescription(
        key=STATE_RUNTIME_DURATION,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        sensor_types=[SensorType.RUNTIME],
        value_fn=lambda logic: logic.runtime_duration.total_seconds(),
    ),
    MaintenanceSensorEntityDescription(
        key=STATE_DEVICE_TURN_ON_COUNT,
        state_class=SensorStateClass.TOTAL_INCREASING,
        sensor_types=[SensorType.COUNT],
        value_fn=lambda logic: logic.device_turn_on_count,
    ),
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the sensor platform."""

    logic: MaintenanceLogic = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        MaintenanceDurationSensorEntity(logic, entry.unique_id, sensor_description)
        for sensor_description in MAINTENANCE_SENSORS if logic.sensor_type in sensor_description.sensor_types
    ])

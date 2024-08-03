"""The binary sensor for the Device Maintenance Monitor integration."""
from dataclasses import dataclass
from datetime import datetime
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback, split_entity_id
from homeassistant.helpers import start
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.helpers.restore_state import RestoredExtraData, RestoreEntity

from .const import (
    DOMAIN,
    ENTITY_BINARY_SENSOR_KEY,
    ENTITY_BINARY_SENSOR_TRANSLATION_KEY,
    SIGNAL_SENSOR_STATE_CHANGE,
)
from .device_binding import get_device_info
from .logics import MaintenanceLogic

_LOGGER = logging.getLogger(__name__)


# TODO: Register services
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the binary sensor platform."""

    logic: MaintenanceLogic = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        MaintenanceNeededBinarySensorEntity(logic, entry.unique_id),
    ])


@dataclass(frozen=True, kw_only=True)
class MaintenanceBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing binary sensors entities."""


class MaintenanceNeededBinarySensorEntity(BinarySensorEntity, RestoreEntity):
    """A class that represents a binary sensor entity for indicating whether maintenance is needed."""

    def __init__(self, logic: MaintenanceLogic, unique_id: str):
        """Initialize the binary sensor entity.

        :param logic: The maintenance logic to be  used.
        """
        self.entity_description = MaintenanceBinarySensorEntityDescription(
            key=ENTITY_BINARY_SENSOR_KEY,
            has_entity_name=True,
            translation_key=ENTITY_BINARY_SENSOR_TRANSLATION_KEY,
            device_class=BinarySensorDeviceClass.PROBLEM,
        )
        self._attr_unique_id = f"{unique_id}_maintenance_needed"
        self._attr_device_info = get_device_info(logic.source_entity)

        object_id = split_entity_id(logic.source_entity.entity_id)[1]
        self.entity_id = f"binary_sensor.{object_id}_maintenance_needed"

        self._logic = logic

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        _LOGGER.info(
            "Adding binary sensor entity '%s' for device '%s' using %s sensor type",
            self.entity_id,
            self._logic.source_entity.entity_id,
            self._logic.sensor_type,
        )
        restored_last_extra_data = await self.async_get_last_extra_data()
        if restored_last_extra_data is not None:
            _LOGGER.info(
                "Restoring state for binary sensor entity '%s' for device '%s', restored state: %s",
                self.entity_id,
                self._logic.source_entity.entity_id,
                restored_last_extra_data.as_dict(),
            )
            self._logic.restore_state(restored_last_extra_data.as_dict())

        @callback
        def initial_update_listener(hass: HomeAssistant) -> None:
            """Handle the initial update after start."""
            current_state = self.hass.states.get(self._logic.source_entity.entity_id)
            _LOGGER.info(
                "Handling initial update for binary sensor entity '%s' for device '%s', state: %s",
                self.entity_id,
                self._logic.source_entity.entity_id,
                current_state,
            )
            if not current_state:
                return
            self._logic.handle_startup(current_state.state)
            self.async_write_ha_state()

        self.async_on_remove(start.async_at_start(self.hass, initial_update_listener))

        @callback
        def source_entity_state_listener(event: Event) -> None:
            old_state = event.data.get("old_state")
            new_state = event.data.get("new_state")
            _LOGGER.info(
                "Handling state change for binary sensor entity '%s' for device '%s', old state: %s, new state: %s",
                self.entity_id,
                self._logic.source_entity.entity_id,
                old_state,
                new_state,
            )

            if old_state is None or new_state is None:
                return

            self._logic.handle_source_entity_state_change(
                old_state.state, new_state.state
            )
            self.async_write_ha_state()

        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                self._logic.source_entity.entity_id,
                source_entity_state_listener,
            ),
        )

        @callback
        def signal_sensor_state_change_listener() -> None:
            """Handle the sensor state change signal."""
            _LOGGER.info(
                "Handling sensor state change for binary sensor entity '%s' for device '%s'",
                self.entity_id,
                self._logic.source_entity.entity_id,
            )
            self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_SENSOR_STATE_CHANGE,
                signal_sensor_state_change_listener,
            )
        )

        if self._logic.update_frequency:
            @callback
            def async_update(__: datetime | None = None) -> None:
                """Update the entity."""
                _LOGGER.info(
                    "Updating binary sensor entity '%s' for device '%s' based on the update frequency (%s)",
                    self.entity_id,
                    self._logic.source_entity.entity_id,
                    str(self._logic.update_frequency),
                )
                self._logic.update()
                self.async_schedule_update_ha_state(True)

            self.async_on_remove(
                async_track_time_interval(
                    self.hass, async_update, self._logic.update_frequency
                )
            )

    async def async_will_remove_from_hass(self) -> None:
        """Handle entity being removed from hass."""
        _LOGGER.info(
            "Removing binary sensor entity '%s' for device '%s', saving state: %s",
            self.entity_id,
            self._logic.source_entity.entity_id,
            self.extra_restore_state_data.as_dict(),
        )
        self._logic.update()
        self.async_write_ha_state()

    @property
    def is_on(self):
        """Return the state of the binary sensor."""
        return self._logic.is_maintenance_needed

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._logic.get_state()

    @property
    def extra_restore_state_data(self) -> RestoredExtraData:
        """Return the state attributes."""
        return RestoredExtraData(self._logic.get_state())

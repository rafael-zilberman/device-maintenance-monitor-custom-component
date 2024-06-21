import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.core import HomeAssistant, Event, callback
from homeassistant.helpers import start
from homeassistant.helpers.dispatcher import async_dispatcher_send, async_dispatcher_connect
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_interval
from homeassistant.helpers.restore_state import RestoreEntity, ExtraStoredData, RestoredExtraData

from .const import DOMAIN, SIGNAL_SENSOR_STATE_CHANGE
from .device_binding import get_device_info
from .logics import MaintenanceLogic

_LOGGER = logging.getLogger(__name__)


# TODO: Register services
async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    _LOGGER.info(f"Setting up entry {entry.entry_id} (binary sensors)")
    logic: MaintenanceLogic = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        MaintenanceNeededBinarySensorEntity(logic),
    ])


@dataclass(frozen=True, kw_only=True)
class MaintenanceBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing binary sensors entities."""


class MaintenanceNeededBinarySensorEntity(BinarySensorEntity, RestoreEntity):
    def __init__(self, logic: MaintenanceLogic):
        self.entity_description = MaintenanceBinarySensorEntityDescription(
            key="maintenance_needed",
            has_entity_name=True,
            translation_key="maintenance_needed",
        )
        self._attr_unique_id = f"{logic.source_entity.entity_id}_maintenance_needed"
        self._attr_device_info = get_device_info(logic.source_entity)

        self._logic = logic

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        restored_last_extra_data = await self.async_get_last_extra_data()
        if restored_last_extra_data is not None:
            self._logic.restore_state(restored_last_extra_data.as_dict())
            _LOGGER.info(
                f"Restored state for {self._logic.source_entity.entity_id}: {restored_last_extra_data.as_dict()}")

        @callback
        def initial_update_listener(hass: HomeAssistant) -> None:
            current_state = self.hass.states.get(self._logic.source_entity.entity_id)
            _LOGGER.info(f"Initial update for {self._logic.source_entity.entity_id}: {current_state}")
            if not current_state:
                return
            self._logic.handle_startup(current_state.state)
            self.async_write_ha_state()

        self.async_on_remove(
            start.async_at_start(self.hass, initial_update_listener)
        )

        @callback
        def source_entity_state_listener(event: Event) -> None:
            old_state = event.data.get('old_state')
            new_state = event.data.get('new_state')

            _LOGGER.info(f"State change for {self._logic.source_entity.entity_id}: {old_state} -> {new_state}")

            if old_state is None or new_state is None:
                return

            self._logic.handle_source_entity_state_change(old_state.state, new_state.state)
            self.async_write_ha_state()

        _LOGGER.info(f"Listening for state changes for {self._logic.source_entity.entity_id}")
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                self._logic.source_entity.entity_id,
                source_entity_state_listener,
            ),
        )

        @callback
        def signal_sensor_state_change_listener() -> None:
            _LOGGER.info(f"Received signal for {self._logic.source_entity.entity_id}")
            self.async_write_ha_state()

        _LOGGER.info(f"Listening for signal for {self._logic.source_entity.entity_id}")
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
                self.async_schedule_update_ha_state(True)

            self.async_on_remove(
                async_track_time_interval(self.hass, async_update, self._logic.update_frequency)
            )

    @property
    def is_on(self):
        _LOGGER.info(f"Checking if maintenance is needed for {self._logic.source_entity.entity_id}")
        return self._logic.is_maintenance_needed

    @property
    def extra_state_attributes(self):
        return self._logic.get_state()

    @property
    def extra_restore_state_data(self) -> RestoredExtraData:
        return RestoredExtraData(self._logic.get_state())

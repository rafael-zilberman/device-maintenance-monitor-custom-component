from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant, callback
from .const import DOMAIN, CONF_DEVICE, CONF_HOURS


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    device = data[CONF_DEVICE]
    hours = data[CONF_HOURS]

    async_add_entities([FilterNeedsReplacementBinarySensor(hass, device, hours)])


class FilterNeedsReplacementBinarySensor(BinarySensorEntity):
    def __init__(self, hass, device, hours):
        self._hass = hass
        self._device = device
        self._hours = hours
        self._total_running_hours = 0
        self._state = False

    @property
    def name(self):
        return f"{self._device} Filter Needs Replacement"

    @property
    def is_on(self):
        return self._state

    async def async_added_to_hass(self):
        self._total_hours_sensor = f"sensor.{self._device}_total_filter_running_hours"
        self._state = await self._calculate_state()
        self.async_on_remove(
            self._hass.states.async_track_state_change(
                self._total_hours_sensor, self._state_changed_callback
            )
        )

    async def _calculate_state(self):
        total_hours_sensor = self._hass.states.get(self._total_hours_sensor)
        if total_hours_sensor:
            total_hours = float(total_hours_sensor.state)
            return total_hours >= self._hours
        return False

    @callback
    def _state_changed_callback(self, entity, old_state, new_state):
        self._hass.async_create_task(self._update_state())

    async def _update_state(self):
        new_state = await self._calculate_state()
        if new_state != self._state:
            self._state = new_state
            self.async_write_ha_state()

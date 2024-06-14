from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from datetime import datetime
from .const import DOMAIN, CONF_DEVICE


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    device = data[CONF_DEVICE]

    async_add_entities([ResetFilterButton(hass, device)])


class ResetFilterButton(ButtonEntity):
    def __init__(self, hass, device):
        self._hass = hass
        self._device = device

    @property
    def name(self):
        return f"{self._device} Reset Filter"

    async def async_added_to_hass(self):
        self._last_replacement_sensor = f"sensor.{self._device}_last_filter_replacement_date"
        self._total_hours_sensor = f"sensor.{self._device}_total_filter_running_hours"
        self._average_hours_sensor = f"sensor.{self._device}_average_usage_hours_per_day"

    async def async_press(self):
        # Reset the filter metrics
        await self._reset_last_replacement_date()
        await self._reset_total_running_hours()
        await self._reset_average_usage_hours_per_day()

    async def _reset_last_replacement_date(self):
        new_date = datetime.now().strftime('%Y-%m-%d')
        await self._hass.states.async_set(self._last_replacement_sensor, new_date)

    async def _reset_total_running_hours(self):
        await self._hass.states.async_set(self._total_hours_sensor, '0')

    async def _reset_average_usage_hours_per_day(self):
        await self._hass.states.async_set(self._average_hours_sensor, '0')

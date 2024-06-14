from datetime import datetime
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.const import STATE_ON, STATE_OFF
from .const import DOMAIN, CONF_DEVICE, CONF_HOURS


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    device = data[CONF_DEVICE]
    hours = data[CONF_HOURS]

    async_add_entities([
        LastDeviceMaintenanceDateSensor(hass, device),
        TotalDeviceRunningHoursSensor(hass, device),
        RemainingHoursUntilDeviceMaintenanceSensor(hass, device, hours),
        AverageUsageHoursPerDaySensor(hass, device),
    ])


class LastDeviceMaintenanceDateSensor(SensorEntity, RestoreEntity):
    def __init__(self, hass, device):
        self._hass = hass
        self._device = device
        self._state = None

    @property
    def name(self):
        return f"{self._device} Last Device Maintenance Date"

    @property
    def state(self):
        return self._state

    async def async_added_to_hass(self):
        last_state = await self.async_get_last_state()
        if last_state:
            self._state = last_state.state
        else:
            self._state = datetime.now().strftime('%Y-%m-%d')

    def update(self):
        pass


class TotalDeviceRunningHoursSensor(SensorEntity, RestoreEntity):
    def __init__(self, hass, device):
        self._hass = hass
        self._device = device
        self._total_running_hours = 0
        self._last_on_time = None
        self._state = None

    @property
    def name(self):
        return f"{self._device} Total Device Running Hours"

    @property
    def state(self):
        return self._total_running_hours

    async def async_added_to_hass(self):
        last_state = await self.async_get_last_state()
        if last_state:
            self._total_running_hours = float(last_state.state)

        async_track_state_change(self._hass, self._device, self._state_changed)

    @callback
    def _state_changed(self, entity_id, old_state, new_state):
        if old_state is None or new_state is None:
            return

        if old_state.state == STATE_OFF and new_state.state == STATE_ON:
            self._last_on_time = datetime.now()
        elif old_state.state == STATE_ON and new_state.state == STATE_OFF and self._last_on_time:
            elapsed_time = (datetime.now() - self._last_on_time).total_seconds() / 3600.0
            self._total_running_hours += elapsed_time
            self._last_on_time = None
            self.async_write_ha_state()

    def update(self):
        pass


class RemainingHoursUntilDeviceMaintenanceSensor(SensorEntity):
    def __init__(self, hass, device, hours):
        self._hass = hass
        self._device = device
        self._hours = hours
        self._state = None

    @property
    def name(self):
        return f"{self._device} Remaining Hours Until Device Maintenance"

    @property
    def state(self):
        total_hours_sensor = self._hass.states.get(f"sensor.{self._device}_total_device_running_hours")
        if total_hours_sensor:
            total_hours = float(total_hours_sensor.state)
            remaining_hours = self._hours - total_hours
            self._state = max(0, remaining_hours)
        return self._state

    def update(self):
        pass


class AverageUsageHoursPerDaySensor(SensorEntity, RestoreEntity):
    def __init__(self, hass, device):
        self._hass = hass
        self._device = device
        self._state = None
        self._total_days = 1

    @property
    def name(self):
        return f"{self._device} Average Usage Hours Per Day"

    @property
    def state(self):
        total_hours_sensor = self._hass.states.get(f"sensor.{self._device}_total_device_running_hours")
        if total_hours_sensor:
            total_hours = float(total_hours_sensor.state)
            self._state = total_hours / self._total_days
        return self._state

    async def async_added_to_hass(self):
        last_state = await self.async_get_last_state()
        if last_state:
            self._total_days = int(last_state.attributes.get("total_days", 1))

    def update(self):
        # Update the total days since the last replacement
        last_maintenance_sensor = self._hass.states.get(f"sensor.{self._device}_last_device_maintenance_date")
        if last_maintenance_sensor:
            last_replacement_date = datetime.strptime(last_maintenance_sensor.state, '%Y-%m-%d')
            self._total_days = (datetime.now() - last_replacement_date).days or 1
        self.async_write_ha_state()

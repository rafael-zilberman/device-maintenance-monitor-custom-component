from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar, List, Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from ..common import SourceEntity
from ..const import SensorType


@dataclass
class MaintenanceData:
    entity_id: str
    name: str
    on_states: Optional[List[str]]


TData = TypeVar('TData', bound=MaintenanceData)


class MaintenanceLogic(ABC, Generic[TData]):
    sensor_type: SensorType

    _hass: HomeAssistant
    _config_entry: ConfigEntry
    _data: TData
    _source_entity: SourceEntity

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, source_entity: SourceEntity):
        self._hass = hass
        self._config_entry = config_entry
        self._data = self._get_logic_data(dict(config_entry.data))
        self._source_entity = source_entity
        self._sensors = []

        self._last_maintenance_date = datetime.now()
        self._last_device_on_time = None
        self._total_runtime_duration = 0

    @abstractmethod
    def _get_logic_data(self, data: dict) -> TData:
        raise NotImplementedError()

    @abstractmethod
    def _get_sensors(self) -> List["MaintenanceSensor"]:
        raise NotImplementedError()

    @abstractmethod
    def is_maintenance_needed(self) -> bool:
        raise NotImplementedError()

    @property
    def source_entity(self) -> SourceEntity:
        return self._source_entity

    @property
    def hass(self) -> HomeAssistant:
        return self._hass

    @property
    def sensors(self) -> List["MaintenanceSensor"]:
        if not self._sensors:
            self._sensors = self._get_sensors()
        return self._sensors

    @property
    def last_maintenance_date(self) -> datetime:
        return self._last_maintenance_date

    def set_last_maintenance_date(self, date: datetime):
        self._last_maintenance_date = date

    @property
    def total_runtime_duration(self) -> int:
        return self._total_runtime_duration

    def set_total_runtime_duration(self, duration: int):
        self._total_runtime_duration = duration

    def reset(self):
        # Reset the last maintenance date to the current date
        self._last_maintenance_date = datetime.now()  # TODO: move defaults to consts

        # Reset the total runtime duration to 0
        self._total_runtime_duration = 0

    def handle_source_entity_state_change(self, old_state: Optional, new_state: Optional):
        is_old_state_on = old_state and old_state in self._data.on_states
        is_new_state_on = new_state and new_state in self._data.on_states
        if is_old_state_on == is_new_state_on:
            # The state hasn't changed
            return

        if is_new_state_on:
            # The device has turned on, store the current time as the last device on time
            self._last_device_on_time = datetime.now()
        elif self._last_device_on_time is not None:
            # The device has turned off, calculate the duration the device was on
            on_duration = (datetime.now() - self._last_device_on_time).total_seconds()
            self._total_runtime_duration += on_duration
            self._last_device_on_time = None

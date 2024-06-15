from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Generic, TypeVar, List, Optional, Dict

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

    _data: TData
    _source_entity: SourceEntity

    def __init__(self, *, config_data: Dict, source_entity: SourceEntity):
        self._data = self._get_logic_data(config_data)
        self._source_entity = source_entity
        self._sensors = []

        self._last_maintenance_date = datetime.now()
        self._last_device_on_time = None
        self._runtime_duration = timedelta(seconds=0)
        self._device_turn_on_count = 0

    @abstractmethod
    def _get_logic_data(self, data: dict) -> TData:
        raise NotImplementedError()

    @abstractmethod
    def _get_sensors(self) -> List["MaintenanceSensor"]:
        raise NotImplementedError()

    @property
    def is_maintenance_needed(self) -> bool:
        raise NotImplementedError()

    @property
    def source_entity(self) -> SourceEntity:
        return self._source_entity

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
    def runtime_duration(self) -> timedelta:
        return self._runtime_duration

    def set_runtime_duration(self, duration: timedelta):
        self._runtime_duration = duration

    @property
    def device_turn_on_count(self) -> int:
        return self._device_turn_on_count

    def set_device_turn_on_count(self, count: int):
        self._device_turn_on_count = count

    def reset(self):
        # Reset the last maintenance date to the current date
        self._last_maintenance_date = datetime.now()  # TODO: move defaults to consts

        # Reset the total runtime duration to 0
        self._runtime_duration = timedelta(seconds=0)

        # Reset the device turn on count to 0
        self._device_turn_on_count = 0

    def handle_source_entity_state_change(self, old_state: Optional, new_state: Optional):
        is_old_state_on = old_state and old_state in self._data.on_states
        is_new_state_on = new_state and new_state in self._data.on_states
        if is_old_state_on == is_new_state_on:
            # The state hasn't changed
            return

        if is_new_state_on:
            # The device has turned on.
            # Store the current time as the last device on time
            self._last_device_on_time = datetime.now()
            # Increment the device turn on count
            self._device_turn_on_count += 1
        elif self._last_device_on_time is not None:
            # The device has turned off, calculate the duration the device was on
            self._runtime_duration += (datetime.now() - self._last_device_on_time)
            self._last_device_on_time = None

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar, List

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from ..common import SourceEntity
from ..const import SensorType


@dataclass
class MaintenanceData:
    entity_id: str
    name: str


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

    @abstractmethod
    def _get_logic_data(self, data: dict) -> TData:
        raise NotImplementedError()

    @abstractmethod
    def get_sensors(self) -> List["MaintenanceSensor"]:
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

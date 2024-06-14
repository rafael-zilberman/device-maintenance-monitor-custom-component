from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar, List

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from ..const import SensorType


@dataclass
class MaintenanceData:
    entity_id: str


TData = TypeVar('TData', bound=MaintenanceData)


class MaintenanceLogic(ABC, Generic[TData]):
    sensor_type: SensorType
    hass: HomeAssistant
    config_entry: ConfigEntry
    data: TData

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        self.hass = hass
        self.config_entry = config_entry
        self.data = self._get_logic_data(dict(config_entry.data))

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
    def source_entity_id(self):
        return self.data.entity_id

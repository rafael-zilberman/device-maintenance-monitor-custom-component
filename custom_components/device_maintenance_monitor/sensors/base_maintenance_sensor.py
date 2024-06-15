from abc import ABC, abstractmethod
from typing import Optional, Generic, TypeVar

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.core import HomeAssistant

from ..common import SourceEntity
from ..logics.base_maintenance_logic import MaintenanceLogic

TState = TypeVar('TState')


class MaintenanceSensor(ABC, Generic[TState]):
    key: str

    def __init__(self, logic: MaintenanceLogic):
        self._logic = logic

    @property
    def id(self) -> str:
        return f"{self._logic.source_entity.entity_id}_{self.key}"

    @property
    def logic(self) -> MaintenanceLogic:
        return self._logic

    @property
    def hass(self) -> HomeAssistant:
        return self.logic.hass

    @property
    def source_entity(self) -> SourceEntity:
        return self.logic.source_entity

    @property
    def device_class(self) -> Optional[SensorDeviceClass]:
        return None

    @property
    def unit_of_measurement(self) -> Optional[str]:
        return None

    @property
    def state(self) -> Optional[TState]:
        return None

    @abstractmethod
    def restore_state(self, state: TState):
        raise NotImplementedError()

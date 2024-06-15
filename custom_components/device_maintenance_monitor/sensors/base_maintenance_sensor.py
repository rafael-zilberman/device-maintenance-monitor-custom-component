from abc import ABC

from homeassistant.core import HomeAssistant

from ..common import SourceEntity
from ..logics.base_maintenance_logic import MaintenanceLogic


class MaintenanceSensor(ABC):
    key: str

    def __init__(self, logic: MaintenanceLogic):
        self._logic = logic

    @property
    def name(self):
        raise NotImplementedError()

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

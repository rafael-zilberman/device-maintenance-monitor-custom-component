from abc import ABC

from ..logics.base_maintenance_logic import MaintenanceLogic


class MaintenanceSensor(ABC):
    key: str

    def __init__(self, logic: MaintenanceLogic):
        self._logic = logic

    @property
    def name(self):
        raise NotImplementedError()

    @property
    def source_entity_id(self):
        return self._logic.source_entity_id

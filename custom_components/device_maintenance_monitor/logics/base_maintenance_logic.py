from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Generic, TypeVar, List, Optional, Dict, final

from ..common import SourceEntity
from ..const import SensorType


@dataclass
class MaintenanceData:
    entity_id: str
    name: str
    on_states: List[str]


TData = TypeVar('TData', bound=MaintenanceData)


class MaintenanceLogic(ABC, Generic[TData]):
    sensor_type: SensorType

    _data: TData
    _source_entity: SourceEntity

    def __init__(self, *, config_data: Dict, source_entity: SourceEntity):
        self._data = self._get_logic_data(config_data)
        self._source_entity = source_entity

        self._last_maintenance_date = datetime.now()
        self._setup()

    def _setup(self):
        pass

    @abstractmethod
    def _get_logic_data(self, data: dict) -> TData:
        raise NotImplementedError()

    @property
    def source_entity(self) -> SourceEntity:
        return self._source_entity

    @final
    def reset(self):
        # Reset the last maintenance date to the current date
        self._last_maintenance_date = datetime.now()  # TODO: move defaults to consts

        self._reset()

    def _reset(self):
        pass

    @final
    def handle_source_entity_state_change(self, old_state: str, new_state: str):
        is_old_state_on = old_state in self._data.on_states
        is_new_state_on = new_state in self._data.on_states
        if is_old_state_on == is_new_state_on:
            # The state hasn't changed
            return

        if is_new_state_on:
            # The device has turned on.
            self._handle_turn_on()
        else:
            # The device has turned off.
            self._handle_turn_off()

    @final
    def handle_startup(self, current_state: str):
        is_current_state_on = current_state in self._data.on_states
        if is_current_state_on:
            # The device is on.
            self._handle_turn_on()
        else:
            # The device is off.
            self._handle_turn_off()

    def _handle_turn_on(self):
        pass

    def _handle_turn_off(self):
        pass

    @property
    def is_maintenance_needed(self) -> bool:
        raise NotImplementedError()

    @final
    def get_state(self) -> Dict[str, str]:
        state = self._get_state()
        state["last_maintenance_date"] = self._last_maintenance_date.strftime(
            '%Y-%m-%d %H:%M:%S')  # TODO: Move to consts
        if self.predicted_maintenance_date:
            state["predicted_maintenance_date"] = self.predicted_maintenance_date.strftime(
                '%Y-%m-%d %H:%M:%S')
        return state

    def _get_state(self) -> Dict[str, str]:
        return {}

    @final
    def restore_state(self, state: Dict[str, str]):
        last_maintenance_date = state.get("last_maintenance_date")  # TODO: Move to consts
        if last_maintenance_date:
            self._last_maintenance_date = datetime.strptime(last_maintenance_date,
                                                            '%Y-%m-%d %H:%M:%S')  # TODO: Move format to consts
        self._restore_state(state)

    def _restore_state(self, state: Dict[str, str]):
        pass

    @property
    def update_frequency(self) -> Optional[timedelta]:
        return

    @property
    def predicted_maintenance_date(self) -> Optional[datetime]:
        return None

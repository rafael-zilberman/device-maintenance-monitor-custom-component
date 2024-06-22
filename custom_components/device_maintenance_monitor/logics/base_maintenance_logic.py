from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Generic, TypeVar, final

from ..common import SourceEntity
from ..const import (
    DATE_FORMAT,
    STATE_LAST_MAINTENANCE_DATE,
    STATE_PREDICTED_MAINTENANCE_DATE,
    SensorType,
)


@dataclass
class MaintenanceData:
    """A data class that represents the maintenance data of a device."""

    entity_id: str  # The unique identifier of the source entity
    name: str  # The name of the entity
    on_states: list[str]  # The states in which the device is considered to be "on"


TData = TypeVar("TData", bound=MaintenanceData)


class MaintenanceLogic(ABC, Generic[TData]):
    """An abstract base class that represents the logic for maintaining a device."""

    sensor_type: SensorType  # The type of sensor used by the configuration

    _data: TData  # The maintenance data
    _source_entity: SourceEntity  # The source entity

    def __init__(self, *, config_data: dict, source_entity: SourceEntity):
        """Initialize a new instance of the MaintenanceLogic class."""
        self._data = self._get_logic_data(config_data)
        self._source_entity = source_entity

        self._last_maintenance_date = datetime.now()  # The date of the last maintenance
        self._setup()

    def _setup(self):
        """Provide additional setup logic."""

    @abstractmethod
    def _get_logic_data(self, data: dict) -> TData:
        """Return the maintenance data for the device.

        :param data: The configuration data of the device.
        :return: The maintenance data of the device.
        """
        raise NotImplementedError

    @property
    def source_entity(self) -> SourceEntity:
        """Returns the source entity of the device."""
        return self._source_entity

    @final
    def reset(self):
        """Reset the last maintenance date to the current date."""
        self._last_maintenance_date = datetime.now()  # TODO: move defaults to consts

        self._reset()

    def _reset(self):
        """Provide additional reset logic."""

    @final
    def handle_source_entity_state_change(self, old_state: str, new_state: str):
        """Handle the state change of the source entity.

        :param old_state: The previous state of the source entity.
        :param new_state: The new state of the source entity.
        """
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
        """Handle the startup of the device.

        :param current_state: The current state of the device.
        """
        is_current_state_on = current_state in self._data.on_states
        if is_current_state_on:
            # The device is on.
            self._handle_turn_on()
        else:
            # The device is off.
            self._handle_turn_off()

    def _handle_turn_on(self):
        """Provide additional logic when the device turns on."""

    def _handle_turn_off(self):
        """Provide additional logic when the device turns off."""

    @property
    @abstractmethod
    def is_maintenance_needed(self) -> bool:
        """Indicate whether maintenance is needed.

        :return: True if maintenance is needed; otherwise, False.
        """
        raise NotImplementedError

    @final
    def get_state(self) -> dict[str, str]:
        """Return the current state of the device.

        :return: The current state of the device.
        """
        state = self._get_state()
        state[STATE_LAST_MAINTENANCE_DATE] = self._last_maintenance_date.strftime(
            DATE_FORMAT
        )
        if self.predicted_maintenance_date:
            state[STATE_PREDICTED_MAINTENANCE_DATE] = (
                self.predicted_maintenance_date.strftime(DATE_FORMAT)
            )
        return state

    def _get_state(self) -> dict[str, str]:
        """Provide additional state to store.

        :return: Additional state to store.
        """
        return {}

    @final
    def restore_state(self, state: dict[str, str]):
        """Restore the state of the device from the given state.

        :param state: The saved state of the device.
        """
        last_maintenance_date = state.get(STATE_LAST_MAINTENANCE_DATE)
        if last_maintenance_date:
            self._last_maintenance_date = datetime.strptime(
                last_maintenance_date, DATE_FORMAT
            )
        self._restore_state(state)

    def _restore_state(self, state: dict[str, str]):
        """Provide additional state restoration logic.

        :param state: The saved state of the device.
        """

    @property
    def update_frequency(self) -> timedelta | None:
        """Return the frequency at which the device should be updated.

        :return: The frequency at which the device should be updated.
        """
        return

    @property
    def predicted_maintenance_date(self) -> datetime | None:
        """Return the predicted date of the next maintenance.

        :return: The predicted date of the next maintenance.
        """
        return None

    def update(self):
        """Provide additional update logic."""

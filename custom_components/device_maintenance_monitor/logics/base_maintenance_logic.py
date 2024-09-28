"""Provides the base class for the maintenance logic of a device."""
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
import logging
from typing import Protocol, final

from ..const import (
    DATE_FORMAT,
    STATE_LAST_MAINTENANCE_DATE,
    STATE_PREDICTED_MAINTENANCE_DATE,
)

_LOGGER = logging.getLogger(__name__)

IsOnExpression = Callable[[], Awaitable[bool]]


class IsMaintenanceNeededExpression(Protocol):
    """An expression to determine if maintenance is needed."""

    def __call__(self,
                 is_maintenance_needed: bool,
                 last_maintenance_date: datetime) -> Awaitable[bool]:
        """Determine if maintenance is needed.

        :param is_maintenance_needed: Whether maintenance is needed.
        :param last_maintenance_date: The date of the last maintenance.
        :return: True if maintenance is needed; otherwise, False.
        """
        ...


class PredictedMaintenanceDateExpression(Protocol):
    """An expression to determine the predicted maintenance date."""

    def __call__(self,
                 predicted_maintenance_date: datetime | None,
                 last_maintenance_date: datetime) -> Awaitable[datetime]:
        """Determine the predicted maintenance date.

        :param predicted_maintenance_date: The date of the last maintenance.
        :param last_maintenance_date: The date of the last maintenance.
        :return: The predicted maintenance date.
        """
        ...


class MaintenanceLogic(ABC):
    """An abstract base class that represents the logic for maintaining a device."""

    _name: str  # The name of the entity
    _entity_id: str | None  # The unique identifier of the source entity
    _on_states: list[str] | None  # The states in which the device is considered to be "on"
    _is_on_expression: IsOnExpression | None  # The expression to determine if the device is on
    _is_maintenance_needed_expression: IsMaintenanceNeededExpression | None  # The expression to determine if maintenance is needed
    _predicted_maintenance_date_expression: PredictedMaintenanceDateExpression | None  # The expression to determine the predicted maintenance date

    def __init__(self, *,
                 name: str,
                 entity_id: str | None,
                 on_states: list[str] | None,
                 is_on_expression: IsOnExpression | None,
                 is_maintenance_needed_expression: IsMaintenanceNeededExpression | None,
                 predicted_maintenance_date_expression: PredictedMaintenanceDateExpression | None):
        """Initialize a new instance of the MaintenanceLogic class.

        :param name: The name of the entity.
        :param entity_id: The unique identifier of the source entity.
        :param on_states: The states in which the device is considered to be "on".
        :param is_on_expression: The expression to determine if the device is on.
        :param is_maintenance_needed_expression: The expression to determine if maintenance is needed.
        :param predicted_maintenance_date_expression: The expression to determine the predicted maintenance date.
        """
        self._name = name
        self._entity_id = entity_id
        self._on_states = on_states
        self._is_on_expression = is_on_expression
        self._is_maintenance_needed_expression = is_maintenance_needed_expression
        self._predicted_maintenance_date_expression = predicted_maintenance_date_expression

        self._last_maintenance_date = datetime.now()  # The date of the last maintenance
        self._last_state_on = False  # The state of the device during the last update
        self._inner_is_maintenance_needed = False  # The inner value of whether maintenance is needed
        self._inner_predicted_maintenance_date = None  # The inner value of the predicted maintenance date

    @classmethod
    def get_instance(cls, config: dict) -> "MaintenanceLogic":
        """Return an instance of the maintenance logic.

        :param config: The configuration data of the device.
        :return: An instance of the maintenance logic.
        """
        raise NotImplementedError

    @property
    def source_entity_id(self) -> str:
        """Returns the source entity of the device."""
        return self._entity_id

    @final
    async def reset(self):
        """Reset the last maintenance date to the current date."""
        self._last_maintenance_date = datetime.now()  # TODO: move defaults to consts

        self._reset()

        # Update the maintenance status
        self._inner_is_maintenance_needed = await self._get_is_maintenance_needed()
        self._inner_predicted_maintenance_date = await self._get_predicted_maintenance_date()

    def _reset(self):
        """Provide additional reset logic."""

    async def _is_device_on(self, state: str) -> bool:
        """Return whether the device is on.

        :return: True if the device is on; otherwise, False.
        """
        if self._is_on_expression:
            return await self._is_on_expression()
        return state in self._on_states

    @final
    async def handle_source_entity_state_change(self, old_state: str, new_state: str):
        """Handle the state change of the source entity.

        :param old_state: The previous state of the source entity.
        :param new_state: The new state of the source entity.
        """
        is_new_state_on = await self._is_device_on(new_state)
        _LOGGER.info(
            "Handling state change for device '%s', old state: %s, new state: %s (%s)",
            self._name,
            old_state,
            new_state,
            is_new_state_on,
        )
        if is_new_state_on == self._last_state_on:
            # The state hasn't changed
            return

        await self._handle_device_state(is_new_state_on)

    @final
    async def handle_startup(self, current_state: str):
        """Handle the startup of the device.

        :param current_state: The current state of the device.
        """
        is_current_state_on = await self._is_device_on(current_state)
        await self._handle_device_state(is_current_state_on)

    async def _handle_device_state(self, state: bool):
        """Handle the state of the device.

        :param state: The state of the device.
        """
        if state:
            # The device is on.
            self._handle_turn_on()
            self._last_state_on = True
        else:
            # The device is off.
            self._handle_turn_off()
            self._last_state_on = False

        # Update the maintenance status
        self._inner_is_maintenance_needed = await self._get_is_maintenance_needed()
        self._inner_predicted_maintenance_date = await self._get_predicted_maintenance_date()

    def _handle_turn_on(self):
        """Provide additional logic when the device turns on."""

    def _handle_turn_off(self):
        """Provide additional logic when the device turns off."""

    async def _get_is_maintenance_needed(self) -> bool:
        """Indicate whether maintenance is needed.

        :return: True if maintenance is needed; otherwise, False.
        """
        inner_is_maintenance_needed = self._is_maintenance_needed
        _LOGGER.info(
            "Checking if maintenance is needed for device '%s': %s",
            self._name,
            inner_is_maintenance_needed,
        )
        if not self._is_maintenance_needed_expression:
            return inner_is_maintenance_needed
        expression_result = await self._is_maintenance_needed_expression(
            is_maintenance_needed=inner_is_maintenance_needed,
            last_maintenance_date=self._last_maintenance_date,
        )
        if expression_result is not None:
            return expression_result
        return inner_is_maintenance_needed

    @property
    def is_maintenance_needed(self) -> bool:
        """Indicate whether maintenance is needed.

        :return: True if maintenance is needed; otherwise, False.
        """
        # This property is updated when the source entity changes state. This used to support async operations.
        return self._inner_is_maintenance_needed

    @property
    @abstractmethod
    def _is_maintenance_needed(self) -> bool:
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
        if self.is_maintenance_needed:
            state[STATE_PREDICTED_MAINTENANCE_DATE] = datetime.now().strftime(DATE_FORMAT)
        elif self.predicted_maintenance_date:
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

    async def _get_predicted_maintenance_date(self) -> datetime | None:
        """Return the predicted date of the next maintenance.

        :return: The predicted date of the next maintenance.
        """
        inner_predicted_maintenance_date = self._predicted_maintenance_date
        if not self._predicted_maintenance_date_expression:
            return inner_predicted_maintenance_date
        expression_result = await self._predicted_maintenance_date_expression(
            predicted_maintenance_date=inner_predicted_maintenance_date,
            last_maintenance_date=self._last_maintenance_date,
        )
        if expression_result is not None:
            return expression_result
        return inner_predicted_maintenance_date

    @property
    def predicted_maintenance_date(self) -> datetime | None:
        """Return the predicted date of the next maintenance.

        :return: The predicted date of the next maintenance.
        """
        # This property is updated when the source entity changes state. This used to support async operations.
        return self._inner_predicted_maintenance_date

    @property
    def _predicted_maintenance_date(self) -> datetime | None:
        """Return the predicted date of the next maintenance.

        :return: The predicted date of the next maintenance.
        """
        return None

    async def update(self):
        """Provide additional update logic."""
        self._update()

        # Update the maintenance status
        self._inner_predicted_maintenance_date = await self._get_predicted_maintenance_date()

    def _update(self):
        """Provide additional update logic."""

    @final
    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @final
    @property
    def logic_type(self) -> str:
        """Return the type of the logic."""
        return self.__class__.__name__

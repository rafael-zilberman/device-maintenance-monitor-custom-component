"""The logics module for device maintenance monitor."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.template import Template

from ..const import CONF_INTERVAL, CONF_IS_ON_TEMPLATE, CONF_SENSOR_TYPE
from .base_maintenance_logic import MaintenanceLogic
from .count_maintenance_logic import CountMaintenanceLogic
from .fixed_interval_maintenance_logic import FixedIntervalMaintenanceLogic
from .runtime_maintenance_logic import RuntimeMaintenanceLogic

IMPLEMENTED_LOGICS: list[type[MaintenanceLogic]] = [
    RuntimeMaintenanceLogic,
    CountMaintenanceLogic,
    FixedIntervalMaintenanceLogic,
]

_LOGGER = logging.getLogger(__name__)


async def get_maintenance_logic(
        hass: HomeAssistant, config_entry: ConfigEntry
) -> MaintenanceLogic:
    """Get the maintenance logic for the config entry.

    :param hass: The Home Assistant instance.
    :param config_entry: The config entry.
    :return: The maintenance logic.
    """
    sensor_type = config_entry.data.get(CONF_SENSOR_TYPE)
    if sensor_type is None:
        raise ValueError(f"{CONF_SENSOR_TYPE} is required in {config_entry.data}")

    config_data = dict(config_entry.data)
    interval = config_data.get(CONF_INTERVAL)
    if interval is not None:
        config_data[CONF_INTERVAL] = cv.time_period_dict(config_data.get(CONF_INTERVAL))

    is_on_template_str: str | None = config_data.get(CONF_IS_ON_TEMPLATE)
    if is_on_template_str is not None:
        is_on_template = Template(is_on_template_str, hass)

        async def render_is_on_template() -> bool:
            return is_on_template.async_render()

        config_data[CONF_IS_ON_TEMPLATE] = render_is_on_template

    for logic in IMPLEMENTED_LOGICS:
        if logic.sensor_type == sensor_type:
            return logic.get_instance(config_data)

    raise NotImplementedError(f"sensor_type {sensor_type} is not implemented")

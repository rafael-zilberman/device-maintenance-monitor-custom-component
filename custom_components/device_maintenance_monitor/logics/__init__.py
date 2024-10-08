"""The logics module for device maintenance monitor."""
from datetime import datetime
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import TemplateError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.template import Template

from ..const import (
    CONF_INTERVAL,
    CONF_IS_ON_TEMPLATE,
    CONF_MAX_INTERVAL,
    CONF_MIN_INTERVAL,
    CONF_SENSOR_TYPE,
    CONFIG_INITIAL_LAST_MAINTENANCE_DATE,
    DATE_FORMAT,
    SensorType,
)
from .base_maintenance_logic import IsOnExpression, MaintenanceLogic
from .count_maintenance_logic import CountMaintenanceLogic
from .fixed_interval_maintenance_logic import FixedIntervalMaintenanceLogic
from .runtime_maintenance_logic import RuntimeMaintenanceLogic

IMPLEMENTED_LOGICS: dict[SensorType, type[MaintenanceLogic]] = {
    SensorType.RUNTIME: RuntimeMaintenanceLogic,
    SensorType.COUNT: CountMaintenanceLogic,
    SensorType.FIXED_INTERVAL: FixedIntervalMaintenanceLogic,
}

_LOGGER = logging.getLogger(__name__)


def _parse_is_on_template(hass: HomeAssistant, is_on_template_str: str) -> IsOnExpression | None:
    """Parse a template string into an expression.

    :param hass: The Home Assistant instance.
    :param is_on_template_str: The template string.
    :return: The expression.
    """
    is_on_template = Template(is_on_template_str, hass)
    if not is_on_template.ensure_valid():
        _LOGGER.error("Error parsing is on template: %s", is_on_template_str)
        return None

    async def render_is_on_template() -> bool:
        try:
            return is_on_template.async_render()
        except TemplateError as e:
            _LOGGER.error("Error rendering is on template: %s", e)
            return False

    return render_is_on_template


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

    # Convert the interval from a time period string to a timedelta
    interval = config_data.get(CONF_INTERVAL)
    if interval is not None:
        config_data[CONF_INTERVAL] = cv.time_period_dict(interval)
    min_interval = config_data.get(CONF_MIN_INTERVAL)
    if min_interval is not None:
        config_data[CONF_MIN_INTERVAL] = cv.time_period_dict(min_interval)
    max_interval = config_data.get(CONF_MAX_INTERVAL)
    if max_interval is not None:
        config_data[CONF_MAX_INTERVAL] = cv.time_period_dict(max_interval)

    # Parse the is_on_template string into an expression
    is_on_template_str: str | None = config_data.get(CONF_IS_ON_TEMPLATE)
    if is_on_template_str:
        config_data[CONF_IS_ON_TEMPLATE] = _parse_is_on_template(hass, is_on_template_str)

    # Convert the date string to a datetime object
    initial_last_maintenance_date_str: str | None = config_data.get(CONFIG_INITIAL_LAST_MAINTENANCE_DATE)
    if initial_last_maintenance_date_str:
        config_data[CONFIG_INITIAL_LAST_MAINTENANCE_DATE] = datetime.strptime(
            initial_last_maintenance_date_str, DATE_FORMAT
        )

    # Get the logic class and create an instance
    logic = IMPLEMENTED_LOGICS.get(sensor_type)
    if not logic:
        raise NotImplementedError(f"sensor_type {sensor_type} is not implemented")

    return logic.get_instance(config_data)

"""The logics module for device maintenance monitor."""
import logging
from datetime import datetime
from typing import Callable, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import TemplateError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.template import Template

from ..const import (
    CONF_INTERVAL,
    CONF_IS_ON_TEMPLATE,
    CONF_MAINTENANCE_NEEDED_TEMPLATE,
    CONF_MAX_INTERVAL,
    CONF_MIN_INTERVAL,
    CONF_PREDICTED_MAINTENANCE_DATE_TEMPLATE,
    CONF_SENSOR_TYPE,
    SensorType, DATE_FORMAT,
)
from .base_maintenance_logic import MaintenanceLogic
from .count_maintenance_logic import CountMaintenanceLogic
from .fixed_interval_maintenance_logic import FixedIntervalMaintenanceLogic
from .runtime_maintenance_logic import RuntimeMaintenanceLogic

IMPLEMENTED_LOGICS: dict[SensorType, type[MaintenanceLogic]] = {
    SensorType.RUNTIME: RuntimeMaintenanceLogic,
    SensorType.COUNT: CountMaintenanceLogic,
    SensorType.FIXED_INTERVAL: FixedIntervalMaintenanceLogic,
}

_LOGGER = logging.getLogger(__name__)


def _parse_template(hass: HomeAssistant,
                    template_str: str,
                    return_parser: Callable[[Any], Any] | None) -> Callable[[...], Any] | None:
    """Parse a template string into an expression.

    :param hass: The Home Assistant instance.
    :param template_str: The template string.
    :param return_parser: The parser to use for the result.
    :return: The expression.
    """
    template = Template(template_str, hass)

    async def render_template(**kwargs) -> Any:
        try:
            result = template.async_render(variables=kwargs)
            if return_parser:
                return return_parser(result)
            return result
        except TemplateError as e:
            _LOGGER.error("Error rendering template: %s", e)
            return None

    return render_template


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
        config_data[CONF_IS_ON_TEMPLATE] = _parse_template(hass, is_on_template_str)

    # Parse the maintenance_needed_template string into an expression
    maintenance_needed_template_str: str | None = config_data.get(CONF_MAINTENANCE_NEEDED_TEMPLATE)
    if maintenance_needed_template_str:
        config_data[CONF_MAINTENANCE_NEEDED_TEMPLATE] = _parse_template(hass, maintenance_needed_template_str)

    # Parse the predicted_maintenance_date_template string into an expression
    predicted_maintenance_date_template_str: str | None = config_data.get(CONF_PREDICTED_MAINTENANCE_DATE_TEMPLATE)
    if predicted_maintenance_date_template_str:
        config_data[CONF_PREDICTED_MAINTENANCE_DATE_TEMPLATE] = _parse_template(
            hass,
            predicted_maintenance_date_template_str,
            return_parser=lambda date_str: datetime.strptime(date_str, DATE_FORMAT),
        )

    # Get the logic class and create an instance
    logic = IMPLEMENTED_LOGICS.get(sensor_type)
    if not logic:
        raise NotImplementedError(f"sensor_type {sensor_type} is not implemented")

    return logic.get_instance(config_data)

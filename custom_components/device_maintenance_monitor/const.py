"""Constants for the Device Maintenance Monitor integration."""
from datetime import timedelta
from enum import StrEnum
from typing import Final

from homeassistant.components.climate import HVACMode

DOMAIN: Final = "device_maintenance_monitor"

# Configuration
CONF_SENSOR_TYPE: Final = "sensor_type"
CONF_ENTITY_ID: Final = "entity_id"
CONF_COUNT: Final = "count"
CONF_INTERVAL: Final = "interval"
CONF_NAME: Final = "name"
CONF_ON_STATES: Final = "on_states"
DEFAULT_ON_STATES: Final = [
    "on",
    HVACMode.DRY,
    HVACMode.COOL,
    HVACMode.HEAT_COOL,
    HVACMode.HEAT,
]  # TODO: Based on the device type
CONF_IS_ON_TEMPLATE: Final = "is_on_template"

# Events
SIGNAL_SENSOR_STATE_CHANGE: Final = "device_maintenance_monitor_sensor_state_change"

# States
STATE_LAST_MAINTENANCE_DATE: Final = "last_maintenance_date"
STATE_PREDICTED_MAINTENANCE_DATE: Final = "predicted_maintenance_date"
STATE_DEVICE_TURN_ON_COUNT: Final = "device_turn_on_count"
STATE_RUNTIME_DURATION: Final = "runtime_duration"

# Services
SERVICE_RESET_MAINTENANCE: Final = "reset_maintenance"

# Entities
ENTITY_BINARY_SENSOR_KEY: Final = "maintenance_needed"
ENTITY_BINARY_SENSOR_TRANSLATION_KEY: Final = "maintenance_needed"
ENTITY_BUTTON_KEY: Final = "reset_maintenance"
ENTITY_BUTTON_TRANSLATION_KEY: Final = "reset_maintenance"

# Formats
DATE_FORMAT: Final = "%Y-%m-%d"

# Other
DEFAULT_FIXED_INTERVAL_UPDATE_FREQUENCY: Final = timedelta(minutes=10)
DEFAULT_RUNTIME_UPDATE_FREQUENCY: Final = timedelta(minutes=1)


class SensorType(StrEnum):
    """Possible modes for a maintenance monitoring."""

    RUNTIME = "runtime"
    COUNT = "count"
    FIXED_INTERVAL = "fixed_interval"

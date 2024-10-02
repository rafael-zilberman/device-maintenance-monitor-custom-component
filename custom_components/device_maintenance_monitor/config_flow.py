"""Config flow for Device Maintenance Monitor integration."""
import copy
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, FlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv, selector
from homeassistant.helpers.entity import get_capability
from homeassistant.helpers.typing import ConfigType

from .common import SourceEntity, create_source_entity
from .const import (
    CONF_COUNT,
    CONF_ENTITY_ID,
    CONF_INTERVAL,
    CONF_IS_ON_TEMPLATE,
    CONF_MAX_INTERVAL,
    CONF_MIN_INTERVAL,
    CONF_NAME,
    CONF_ON_STATES,
    CONF_SENSOR_TYPE,
    CONFIG_INITIAL_LAST_MAINTENANCE_DATE,
    DOMAIN,
    SensorType,
)

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPE_MENU = {
    SensorType.RUNTIME: "Runtime",
    SensorType.COUNT: "Power On Count",
    SensorType.FIXED_INTERVAL: "Fixed Interval",
}

CONFIG_SCHEMA = {
    vol.Optional(CONF_NAME): selector.TextSelector(),
    vol.Optional(CONFIG_INITIAL_LAST_MAINTENANCE_DATE): selector.DateSelector(),
}

OPTIONS_SCHEMA = {
    vol.Optional(CONF_NAME): selector.TextSelector(),
}

SCHEMA_RUNTIME = {
    vol.Required(CONF_ENTITY_ID): selector.EntitySelector(),
    vol.Required(CONF_INTERVAL): selector.DurationSelector(),
    vol.Optional(CONF_MIN_INTERVAL): selector.DurationSelector(
        selector.DurationSelectorConfig(
            enable_day=True,
        ),
    ),
    vol.Optional(CONF_MAX_INTERVAL): selector.DurationSelector(
        selector.DurationSelectorConfig(
            enable_day=True,
        ),
    ),
    vol.Optional(CONF_IS_ON_TEMPLATE): selector.TemplateSelector(),
}

SCHEMA_COUNT = {
    vol.Required(CONF_ENTITY_ID): selector.EntitySelector(),
    vol.Required(CONF_COUNT): selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=1,
            mode=selector.NumberSelectorMode.BOX,
        ),
    ),
    vol.Optional(CONF_IS_ON_TEMPLATE): selector.TemplateSelector(),
}

SCHEMA_FIXED_INTERVAL = {
    vol.Optional(CONF_ENTITY_ID): selector.EntitySelector(),
    vol.Required(CONF_INTERVAL): selector.DurationSelector(
        selector.DurationSelectorConfig(
            enable_day=True,
        ),
    ),
}


def _get_schema_by_sensor_type(sensor_type: SensorType) -> dict:
    if sensor_type == SensorType.RUNTIME:
        return SCHEMA_RUNTIME

    if sensor_type == SensorType.COUNT:
        return SCHEMA_COUNT

    if sensor_type == SensorType.FIXED_INTERVAL:
        return SCHEMA_FIXED_INTERVAL

    raise NotImplementedError(f"Sensor type {sensor_type} is not implemented")


def _validate_min_and_max_interval(user_input: dict) -> bool:
    """Validate that the min interval is less than or equal to the max interval."""
    min_interval = user_input.get(CONF_MIN_INTERVAL)
    max_interval = user_input.get(CONF_MAX_INTERVAL)
    if not min_interval or not max_interval:
        return True
    return cv.time_period_dict(min_interval) <= cv.time_period_dict(max_interval)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Device Maintenance Monitor."""

    VERSION = 1
    MINOR_VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(
            self,
            user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the initial step."""
        return self.async_show_menu(step_id="user", menu_options=SENSOR_TYPE_MENU)

    async def async_step_runtime(
            self,
            user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the runtime logic configuration."""
        errors = {}  # TODO: validate user input
        if user_input is not None:
            if not _validate_min_and_max_interval(user_input):
                errors[CONF_MIN_INTERVAL] = "Minimum interval must be less than or equal to maximum interval"

            if not errors:
                return await self.create_config_entry(SensorType.RUNTIME, user_input)

        return self.async_show_form(
            step_id="runtime",
            data_schema=self._build_setup_schema(SensorType.RUNTIME),
            errors=errors,
            last_step=True,
        )

    async def async_step_count(
            self,
            user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the power on count logic configuration."""
        errors = {}  # TODO: validate user input
        if user_input is not None:
            if not errors:
                return await self.create_config_entry(SensorType.COUNT, user_input)

        return self.async_show_form(
            step_id="count",
            data_schema=self._build_setup_schema(SensorType.COUNT),
            errors=errors,
            last_step=True,
        )

    async def async_step_fixed_interval(
            self,
            user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the fixed interval logic configuration."""
        errors = {}  # TODO: validate user input
        if user_input is not None:
            if not errors:
                return await self.create_config_entry(
                    SensorType.FIXED_INTERVAL, user_input
                )

        return self.async_show_form(
            step_id="fixed_interval",
            data_schema=self._build_setup_schema(SensorType.FIXED_INTERVAL),
            errors=errors,
            last_step=True,
        )

    @staticmethod
    def _build_setup_schema(sensor_type: SensorType):
        schema = vol.Schema(CONFIG_SCHEMA)
        return schema.extend(_get_schema_by_sensor_type(sensor_type))

    @callback
    async def create_config_entry(
            self,
            selected_sensor_type: SensorType,
            user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Create the config entry."""
        source_entity_id = user_input.get(CONF_ENTITY_ID)

        entry_config: ConfigType = copy.copy(user_input)

        # Set unique_id to prevent duplicate entries:
        if source_entity_id:
            source_entity = await create_source_entity(
                source_entity_id,
                self.hass,
            )
            name = user_input.get(CONF_NAME, f"{source_entity.name} Maintenance Monitor")
            source_unique_id = source_entity.unique_id or (source_entity_id.replace(".", "_"))
            await self.async_set_unique_id(f"mm_{source_unique_id}")
        else:
            name = user_input.get(CONF_NAME)
            if not name:
                return self.async_abort(reason="missing_name")
            await self.async_set_unique_id(f"mm_{name.lower().replace(' ', '_')}")
        self._abort_if_unique_id_configured()

        entry_config.update(
            {
                CONF_SENSOR_TYPE: selected_sensor_type,
                CONF_ENTITY_ID: source_entity_id,
                CONF_NAME: name,
            }
        )
        return self.async_create_entry(title=str(name), data=entry_config)


class OptionsFlowHandler(OptionsFlow):
    """Handle an option flow."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.current_config: dict = dict(config_entry.data)
        self.sensor_type: SensorType = self.current_config.get(CONF_SENSOR_TYPE)
        self.source_entity_id: str = self.current_config.get(CONF_ENTITY_ID)
        self.source_entity: SourceEntity | None = None

    async def async_step_init(
            self,
            user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        self.current_config = dict(self.config_entry.data)
        if self.source_entity_id:
            self.source_entity = await create_source_entity(
                self.source_entity_id,
                self.hass,
            )

        schema = self._build_options_schema()
        if user_input is not None:
            errors = await self.save_options(user_input, schema)
            if not errors:
                return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
        )

    async def save_options(
            self,
            user_input: dict[str, Any],
            schema: vol.Schema,
    ) -> dict:
        """Save options, and return errors when validation fails."""
        self._process_user_input(user_input, schema)

        if CONF_ENTITY_ID in user_input:
            self.current_config[CONF_ENTITY_ID] = user_input[CONF_ENTITY_ID]

        errors = {}
        if not _validate_min_and_max_interval(user_input):
            errors[CONF_MIN_INTERVAL] = "Minimum interval must be less than or equal to maximum interval"

        if errors:
            return errors
        self.hass.config_entries.async_update_entry(
            self.config_entry,
            data=self.current_config,
            title=str(self.current_config.get(CONF_NAME)),
        )
        return {}

    def _process_user_input(
            self,
            user_input: dict[str, Any],
            schema: vol.Schema,
    ):
        """Process the provided user input against the schema.

        Update the current_config dictionary with the new options.
        We use that to save the data to config entry later on.
        """
        for key in schema.schema:
            if isinstance(key, vol.Marker):
                key = key.schema
            if key in user_input:
                self.current_config[key] = user_input.get(key)
            elif key in self.current_config:
                self.current_config.pop(key)

    def _build_options_schema(self) -> vol.Schema:
        """Build the options schema. depending on the selected sensor type."""
        schema = vol.Schema(OPTIONS_SCHEMA)
        data_schema = schema.extend(_get_schema_by_sensor_type(self.sensor_type))

        if self.source_entity_id:
            # Get the optional states of the source entity
            options = self._get_source_entity_state_options()
            data_schema = data_schema.extend(
                {
                    vol.Optional(CONF_ON_STATES): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=options,
                        ),
                    ),
                }
            )

        return _fill_schema_defaults(
            data_schema,
            self.current_config,
        )

    def _get_source_entity_state_options(self) -> list[str]:
        """Get the state options of the source entity."""
        for capability in ["hvac_modes", "options"]:
            capabilities = get_capability(self.hass, self.source_entity_id, capability)
            if capabilities:
                return capabilities

        return ["on", "off"]


def _fill_schema_defaults(
        data_schema: vol.Schema,
        current_config: dict[str, str],
) -> vol.Schema:
    """Make a copy of the schema with suggested values set to saved options."""
    schema = {}
    for key, val in data_schema.schema.items():
        new_key = key
        if key in current_config and isinstance(key, vol.Marker):
            if (
                    isinstance(key, vol.Optional)
                    and callable(key.default)
                    and key.default()
            ):
                new_key = vol.Optional(key.schema, default=current_config.get(key))
            else:
                new_key = copy.copy(key)
                new_key.description = {"suggested_value": current_config.get(key)}
        schema[new_key] = val
    return vol.Schema(schema)

import copy
import logging
from typing import Any, Dict

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import FlowResult, OptionsFlow, ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.entity import get_capability
from homeassistant.helpers.typing import ConfigType

from .common import SourceEntity, create_source_entity
from .const import DOMAIN, CONF_ENTITY_ID, CONF_INTERVAL, SensorType, CONF_COUNT, CONF_SENSOR_TYPE, CONF_NAME, \
    CONF_ON_STATES

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPE_MENU = {
    SensorType.RUNTIME: "Runtime",
    SensorType.COUNT: "Power On Count",
    SensorType.FIXED_INTERVAL: "Fixed Interval",
}

SETUP_SCHEMA = {
    vol.Required(CONF_ENTITY_ID): selector.EntitySelector(),
    vol.Optional(CONF_NAME): selector.TextSelector(),
}

CONFIG_SCHEMA = {
    vol.Optional(CONF_NAME): selector.TextSelector(),
}

SCHEMA_RUNTIME = {
    vol.Required(CONF_INTERVAL): selector.DurationSelector(),
}

SCHEMA_COUNT = {
    vol.Required(CONF_COUNT): selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=1,
            mode=selector.NumberSelectorMode.BOX,
        ),
    ),
}

SCHEMA_FIXED_INTERVAL = {
    vol.Required(CONF_INTERVAL): selector.DurationSelector(
        selector.DurationSelectorConfig(
            enable_day=True,
        ),
    ),
}


def _get_schema_by_sensor_type(sensor_type: SensorType) -> Dict:
    if sensor_type == SensorType.RUNTIME:
        return SCHEMA_RUNTIME
    elif sensor_type == SensorType.COUNT:
        return SCHEMA_COUNT
    elif sensor_type == SensorType.FIXED_INTERVAL:
        return SCHEMA_FIXED_INTERVAL
    else:
        raise NotImplementedError(f"Sensor type {sensor_type} is not implemented")


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
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
        errors = {}  # TODO: validate user input
        if user_input is not None:
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
        errors = {}  # TODO: validate user input
        if user_input is not None:
            if not errors:
                return await self.create_config_entry(SensorType.FIXED_INTERVAL, user_input)

        return self.async_show_form(
            step_id="fixed_interval",
            data_schema=self._build_setup_schema(SensorType.FIXED_INTERVAL),
            errors=errors,
            last_step=True,
        )

    def _build_setup_schema(self, sensor_type: SensorType):
        schema = vol.Schema(SETUP_SCHEMA)
        return schema.extend(_get_schema_by_sensor_type(sensor_type))

    @callback
    async def create_config_entry(
            self,
            selected_sensor_type: SensorType,
            user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        _LOGGER.info(f"Creating config entry for sensor type {selected_sensor_type}: {user_input}")

        source_entity_id = user_input.get(CONF_ENTITY_ID)
        if source_entity_id is None:
            return self.async_abort(reason="no_source_entity")

        source_entity = await create_source_entity(
            source_entity_id,
            self.hass,
        )
        name = user_input.get(CONF_NAME, f"{source_entity.name} Maintenance Monitor")

        entry_config: ConfigType = copy.copy(user_input)
        entry_config.update({
            CONF_SENSOR_TYPE: selected_sensor_type,
            CONF_ENTITY_ID: source_entity_id,
            CONF_NAME: name,
        })

        # Set unique_id to prevent duplicate entries:
        source_unique_id = (
                source_entity.unique_id or source_entity_id
        )
        await self.async_set_unique_id(f"maintenance_monitor_{source_unique_id}")
        self._abort_if_unique_id_configured()

        _LOGGER.info(f"Config entry for sensor type {selected_sensor_type}: {entry_config}")
        return self.async_create_entry(title=str(name), data=entry_config)


class OptionsFlowHandler(OptionsFlow):
    """Handle an option flow."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.current_config: dict = dict(config_entry.data)
        self.sensor_type: SensorType = self.current_config.get(CONF_SENSOR_TYPE)
        self.source_entity_id: str = self.current_config.get(CONF_ENTITY_ID)  # type: ignore
        self.source_entity: SourceEntity | None = None

    async def async_step_init(
            self,
            user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle options flow."""
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

        self.hass.config_entries.async_update_entry(
            self.config_entry,
            data=self.current_config,
        )
        return {}

    def _process_user_input(
            self,
            user_input: dict[str, Any],
            schema: vol.Schema,
    ) -> None:
        """
        Process the provided user input against the schema.
        Update the current_config dictionary with the new options. We use that to save the data to config entry later on.
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
        schema = vol.Schema(CONFIG_SCHEMA)
        data_schema = schema.extend(_get_schema_by_sensor_type(self.sensor_type))

        # Get the states of the source entity
        options = ["on", "off"]
        for capability in ["hvac_modes", "options"]:
            capabilities = get_capability(self.hass, self.source_entity_id, capability)
            if capabilities:
                options = capabilities
                break
        _LOGGER.info(f"States: {options}")
        # Add on_states to the schema
        data_schema = data_schema.extend({
            vol.Optional(CONF_ON_STATES): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=options,
                ),
            ),
        })

        return _fill_schema_defaults(
            data_schema,
            self.current_config,
        )


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
                new_key = vol.Optional(key.schema, default=current_config.get(key))  # type: ignore
            else:
                new_key = copy.copy(key)
                new_key.description = {"suggested_value": current_config.get(key)}  # type: ignore
        schema[new_key] = val
    return vol.Schema(schema)

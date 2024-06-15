import copy
import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import FlowResult, OptionsFlow, ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.typing import ConfigType

from .common import SourceEntity, create_source_entity
from .const import DOMAIN, CONF_ENTITY_ID, CONF_INTERVAL, SensorType, CONF_COUNT, CONF_SENSOR_TYPE, CONF_NAME, CONF_ON_STATES

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPE_MENU = {
    SensorType.RUNTIME: "Runtime",
    SensorType.COUNT: "Power On Count",
    SensorType.FIXED_INTERVAL: "Fixed Interval",
}

SCHEMA_RUNTIME = vol.Schema(
    {
        vol.Required(CONF_ENTITY_ID): selector.EntitySelector(),
        vol.Optional(CONF_NAME): selector.TextSelector(),
        vol.Required(CONF_INTERVAL): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=1,
                unit_of_measurement=UnitOfTime.HOURS,
                mode=selector.NumberSelectorMode.BOX,
            ),
        ),
        vol.Optional(CONF_ON_STATES): selector.TextSelector(  # TODO: Use state selector
            selector.TextSelectorConfig(
                multiple=True,
            ),
        ),
    },
)

SCHEMA_COUNT = vol.Schema(
    {
        vol.Required(CONF_ENTITY_ID): selector.EntitySelector(),
        vol.Optional(CONF_NAME): selector.TextSelector(),
        vol.Required(CONF_COUNT): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=1,
                mode=selector.NumberSelectorMode.BOX,
            ),
        ),
        vol.Optional(CONF_ON_STATES): selector.TextSelector(
            selector.TextSelectorConfig(
                multiple=True,
            ),
        ),
    },
)

SCHEMA_FIXED_INTERVAL = vol.Schema(
    {
        vol.Required(CONF_ENTITY_ID): selector.EntitySelector(),
        vol.Optional(CONF_NAME): selector.TextSelector(),
        vol.Required(CONF_INTERVAL): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=1,
                unit_of_measurement=UnitOfTime.DAYS,
                mode=selector.NumberSelectorMode.BOX,
            ),
        ),
        vol.Optional(CONF_ON_STATES): selector.TextSelector(
            selector.TextSelectorConfig(
                multiple=True,
            ),
        ),
    },
)


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
            data_schema=SCHEMA_RUNTIME,
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
            data_schema=SCHEMA_COUNT,
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
            data_schema=SCHEMA_FIXED_INTERVAL,
            errors=errors,
            last_step=True,
        )

    @callback
    async def create_config_entry(
            self,
            selected_sensor_type: SensorType,
            user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        _LOGGER.info(f"Creating config entry for sensor type {selected_sensor_type}: {user_input}")

        source_entity_id = user_input.get(CONF_ENTITY_ID)
        if not source_entity_id:
            return self.async_abort(reason="no_source_entity")

        source_entity = await create_source_entity(
            source_entity_id,
            self.hass,
        )
        name = user_input.get(CONF_NAME, f"{source_entity.name} Maintenance Monitor")

        sensor_config: ConfigType = {
            CONF_SENSOR_TYPE: selected_sensor_type,
            CONF_ENTITY_ID: source_entity_id,
            CONF_NAME: name,
            CONF_ON_STATES: user_input.get(CONF_ON_STATES),
        }

        # Set unique_id to prevent duplicate entries:
        source_unique_id = (
                source_entity.unique_id or source_entity_id
        )
        await self.async_set_unique_id(f"maintenance_monitor_{source_unique_id}")
        self._abort_if_unique_id_configured()

        return self.async_create_entry(title=str(name), data=sensor_config)


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

        schema = self.build_options_schema()
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

    def build_options_schema(self) -> vol.Schema:
        """Build the options schema. depending on the selected sensor type."""
        data_schema: vol.Schema = vol.Schema({})
        if self.sensor_type == SensorType.RUNTIME:
            data_schema = SCHEMA_RUNTIME
        elif self.sensor_type == SensorType.COUNT:
            data_schema = SCHEMA_COUNT
        elif self.sensor_type == SensorType.FIXED_INTERVAL:
            data_schema = SCHEMA_FIXED_INTERVAL
        else:
            raise NotImplementedError(f"Sensor type {self.sensor_type} is not implemented")

        return _fill_schema_defaults(
            data_schema,
            self.current_config,
        )


def _fill_schema_defaults(
        data_schema: vol.Schema,
        options: dict[str, str],
) -> vol.Schema:
    """Make a copy of the schema with suggested values set to saved options."""
    schema = {}
    for key, val in data_schema.schema.items():
        new_key = key
        if key in options and isinstance(key, vol.Marker):
            if (
                    isinstance(key, vol.Optional)
                    and callable(key.default)
                    and key.default()
            ):
                new_key = vol.Optional(key.schema, default=options.get(key))  # type: ignore
            else:
                new_key = copy.copy(key)
                new_key.description = {"suggested_value": options.get(key)}  # type: ignore
        schema[new_key] = val
    return vol.Schema(schema)

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN, CONF_HOURS

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOURS): cv.positive_int,
})


class DeviceMaintenanceMonitorOptionsFlowHandler(config_entries.OptionsFlow):

    def __init__(self, config_entry):
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self.options.update(user_input)
            return self.async_create_entry(title="", data=self.options)

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            description_placeholders={
                "current_hours": self.options.get(CONF_HOURS, 0),
            }
        )

    async def async_step_import(self, user_input: ConfigType):
        if self.config_entry.source == config_entries.SOURCE_IMPORT:
            return await self.async_step_user(user_input)

        return self.async_abort(reason="already_setup")

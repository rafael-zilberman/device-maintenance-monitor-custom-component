import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.translation import gettext
from .const import DOMAIN, CONF_DEVICE, CONF_HOURS


class HVACFilterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            if CONF_DEVICE in user_input:
                return await self._show_hours_form(user_input)
            elif CONF_HOURS in user_input:
                # Validate and finish configuration
                return self._create_entry(user_input)

        return await self._show_device_form(errors)

    async def _show_device_form(self, errors):
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_DEVICE): str,
                vol.Required(CONF_HOURS): cv.positive_int
            }),
            errors=errors,
            description_placeholders={
                "step_title": gettext("config_flow.step.title")
            }
        )

    async def _show_hours_form(self, user_input):
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOURS): cv.positive_int
            }),
            initial_values=user_input,
            errors={}
        )

    def _create_entry(self, user_input):
        return self.async_create_entry(
            title=user_input[CONF_DEVICE],
            data={
                CONF_DEVICE: user_input[CONF_DEVICE],
                CONF_HOURS: user_input[CONF_HOURS]
            }
        )

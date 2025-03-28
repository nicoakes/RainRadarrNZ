from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from .const import DOMAIN

class RainRadarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=self._get_data_schema())

        # Here you can add validation for user_input if needed

        return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

    def _get_data_schema(self):
        from homeassistant.helpers import config_validation as cv
        import voluptuous as vol

        return vol.Schema({
            vol.Required(CONF_NAME, default="Rain Radar"): str,
        })
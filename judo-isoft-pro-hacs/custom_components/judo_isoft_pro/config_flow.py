"""UI-Konfigurations-Ablauf für die Benutzeroberfläche."""
import voluptuous as vol
from homeassistant import config_entries

from .const import (
    DOMAIN,
    CONF_IP_ADDRESS,
    CONF_USERNAME,
    CONF_PASSWORD,
    DEFAULT_USERNAME,
    DEFAULT_PASSWORD,
)

class JudoIsoftConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Behandelt die Eingabe von IP, Benutzername und Passwort."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_IP_ADDRESS])
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(
                title=f"JUDO i-soft ({user_input[CONF_IP_ADDRESS]})",
                data=user_input,
            )

        data_schema = vol.Schema({
            vol.Required(CONF_IP_ADDRESS, default="192.168.2.21"): str,
            vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
            vol.Required(CONF_PASSWORD, default=DEFAULT_PASSWORD): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
"""Config flow for JUDO i-soft PRO / PRO L."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import JudoApi, JudoApiError
from .const import DEFAULT_PASSWORD, DEFAULT_PORT, DEFAULT_USERNAME, DOMAIN


class JudoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle JUDO setup with a device name and multiple config entries."""

    VERSION = 1

    async def async_step_reconfigure(
        self, user_input: dict | None = None
    ) -> dict:
        """Change the device name without replacing the config entry."""
        entry = self._get_reconfigure_entry()
        if user_input is not None:
            name = str(user_input[CONF_NAME]).strip()
            if not name:
                return self.async_show_form(
                    step_id="reconfigure",
                    data_schema=vol.Schema(
                        {vol.Required(CONF_NAME, default=entry.data.get(CONF_NAME, entry.title)): str}
                    ),
                    errors={"base": "invalid_name"},
                )
            return self.async_update_reload_and_abort(
                entry, data_updates={CONF_NAME: name}, title=name
            )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {vol.Required(CONF_NAME, default=entry.data.get(CONF_NAME, entry.title)): str}
            ),
        )

    async def async_step_user(self, user_input: dict | None = None) -> dict:
        errors: dict[str, str] = {}
        if user_input is not None:
            name = str(user_input[CONF_NAME]).strip()
            host = str(user_input[CONF_HOST]).strip()
            port = int(user_input[CONF_PORT])
            username = str(user_input[CONF_USERNAME])
            password = str(user_input[CONF_PASSWORD])

            if not name:
                errors["base"] = "invalid_name"
            else:
                await self.async_set_unique_id(f"{host}:{port}")
                self._abort_if_unique_id_configured()

                api = JudoApi(
                    async_get_clientsession(self.hass),
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                )
                try:
                    await api.test_connection()
                except JudoApiError:
                    errors["base"] = "cannot_connect"
                else:
                    return self.async_create_entry(
                        title=name,
                        data={
                            CONF_NAME: name,
                            CONF_HOST: host,
                            CONF_PORT: port,
                            CONF_USERNAME: username,
                            CONF_PASSWORD: password,
                        },
                    )

        schema = vol.Schema(
            {
                # Name intentionally comes first: it becomes the Home Assistant
                # device name and lets several JUDO installations be kept apart.
                vol.Required(CONF_NAME, default="JUDO i-soft PRO"): str,
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=65535)
                ),
                vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
                vol.Required(CONF_PASSWORD, default=DEFAULT_PASSWORD): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

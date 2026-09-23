"""Config flow for JUDO i-soft PRO / PRO L."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import JudoApi, JudoApiError
from .const import DEFAULT_PASSWORD, DEFAULT_PORT, DEFAULT_USERNAME, DOMAIN


class JudoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle JUDO setup."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = str(user_input[CONF_HOST]).strip()
            port = int(user_input[CONF_PORT])
            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()

            api = JudoApi(
                async_get_clientsession(self.hass),
                host=host,
                port=port,
                username=str(user_input[CONF_USERNAME]),
                password=str(user_input[CONF_PASSWORD]),
            )
            try:
                await api.test_connection()
            except JudoApiError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=f"JUDO i-soft PRO ({host})",
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_USERNAME: str(user_input[CONF_USERNAME]),
                        CONF_PASSWORD: str(user_input[CONF_PASSWORD]),
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=65535)
                ),
                vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
                vol.Required(CONF_PASSWORD, default=DEFAULT_PASSWORD): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

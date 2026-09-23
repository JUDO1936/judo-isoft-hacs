"""Config flow for JUDO i-soft PRO / PRO L."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_PORT, CONF_USERNAME

from .const import CMD_DEVICE_NUMBER, DEFAULT_PASSWORD, DEFAULT_PORT, DEFAULT_USERNAME, DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle setup and reconfiguration of JUDO i-soft PRO devices."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            name = str(user_input.get(CONF_NAME, "")).strip()
            host = str(user_input.get(CONF_HOST, "")).strip()

            if not name:
                errors["base"] = "invalid_name"
            elif not host:
                errors["base"] = "invalid_host"
            else:
                try:
                    port = int(user_input.get(CONF_PORT, DEFAULT_PORT))
                except (TypeError, ValueError):
                    errors["base"] = "invalid_port"
                    port = DEFAULT_PORT

                if not errors:
                    try:
                        # Import the API only after the config-flow handler is
                        # already registered and the user has submitted data.
                        from homeassistant.helpers.aiohttp_client import async_get_clientsession
                        from .api import JudoApi, JudoApiError

                        api = JudoApi(
                            async_get_clientsession(self.hass),
                            host=host,
                            port=port,
                            username=str(user_input.get(CONF_USERNAME, DEFAULT_USERNAME)),
                            password=str(user_input.get(CONF_PASSWORD, DEFAULT_PASSWORD)),
                        )
                        await api.test_connection()
                        device_number = await api.read(CMD_DEVICE_NUMBER)
                    except (JudoApiError, OSError, ValueError):
                        errors["base"] = "cannot_connect"
                    else:
                        if device_number:
                            await self.async_set_unique_id(
                                f"judo-{device_number.upper()}"
                            )
                            self._abort_if_unique_id_configured()

                        return self.async_create_entry(
                            title=name,
                            data={
                                CONF_NAME: name,
                                CONF_HOST: host,
                                CONF_PORT: port,
                                CONF_USERNAME: str(user_input.get(CONF_USERNAME, DEFAULT_USERNAME)),
                                CONF_PASSWORD: str(user_input.get(CONF_PASSWORD, DEFAULT_PASSWORD)),
                            },
                        )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default="JUDO i-soft PRO"): str,
                vol.Required(CONF_HOST): str,
                vol.Required(
                    CONF_PORT, default=DEFAULT_PORT
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
                vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
                vol.Required(CONF_PASSWORD, default=DEFAULT_PASSWORD): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        """Change the configured device name without creating a new entry."""
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            name = str(user_input.get(CONF_NAME, "")).strip()
            if not name:
                return self.async_show_form(
                    step_id="reconfigure",
                    data_schema=vol.Schema(
                        {
                            vol.Required(
                                CONF_NAME,
                                default=entry.data.get(CONF_NAME, entry.title),
                            ): str
                        }
                    ),
                    errors={"base": "invalid_name"},
                )

            return self.async_update_reload_and_abort(
                entry,
                data_updates={CONF_NAME: name},
                title=name,
            )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NAME,
                        default=entry.data.get(CONF_NAME, entry.title),
                    ): str
                }
            ),
        )

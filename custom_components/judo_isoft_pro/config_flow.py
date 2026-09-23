"""Config flow for JUDO i-soft PRO / PRO L."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_PORT, CONF_USERNAME

from .const import DEFAULT_PASSWORD, DEFAULT_PORT, DEFAULT_USERNAME, DOMAIN, CMD_DEVICE_NUMBER


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle setup and reconfiguration of JUDO i-soft PRO devices."""

    VERSION = 1

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        """Change the configured device name without creating another entry."""
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            name = str(user_input[CONF_NAME]).strip()
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

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        """Handle the initial user setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            name = str(user_input[CONF_NAME]).strip()
            host = str(user_input[CONF_HOST]).strip()
            port = int(user_input[CONF_PORT])
            username = str(user_input[CONF_USERNAME])
            password = str(user_input[CONF_PASSWORD])

            if not name:
                errors["base"] = "invalid_name"
            elif not host:
                errors["base"] = "invalid_host"
            else:
                # Keep third-party imports out of module import time. This is
                # important for Home Assistant's config-flow discovery: the
                # handler must register even before the API client is needed.
                from homeassistant.helpers.aiohttp_client import async_get_clientsession
                from .api import JudoApi, JudoApiError

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
                    # The JUDO documentation defines command 06 as the stable
                    # device number. Use it as a unique ID when available so
                    # multiple physical devices can be configured while the
                    # same physical device is not accidentally added twice.
                    try:
                        device_number = await api.read(CMD_DEVICE_NUMBER)
                    except JudoApiError:
                        device_number = ""

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
                            CONF_USERNAME: username,
                            CONF_PASSWORD: password,
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

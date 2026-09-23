"""JUDO i-soft PRO / L Home Assistant Integration."""
import logging

import requests
import voluptuous as vol
from requests.auth import HTTPBasicAuth

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .api import request
from .const import DOMAIN, CONF_IP_ADDRESS, CONF_USERNAME, CONF_PASSWORD

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor", "number", "button"]

SERVICES_REGISTERED = "services_registered"

SERVICE_SET_HARDNESS_SCHEMA = vol.Schema({
    vol.Required("haerte"): vol.All(vol.Coerce(int), vol.Range(min=0, max=30)),
    vol.Optional("entry_id"): cv.string,
})
SERVICE_SET_SCENE_SCHEMA = vol.Schema({
    vol.Required("szene"): vol.All(vol.Coerce(int), vol.Range(min=0, max=10)),
    vol.Required("dauer_hex"): str,
    vol.Optional("entry_id"): cv.string,
})
SERVICE_SET_DAYS_SCHEMA = vol.Schema({
    vol.Required("tage"): vol.All(vol.Coerce(int), vol.Range(min=1, max=30)),
    vol.Optional("entry_id"): cv.string,
})
SERVICE_SET_VOLUME_SCHEMA = vol.Schema({
    vol.Required("liter"): vol.All(vol.Coerce(int), vol.Range(min=100, max=3000)),
    vol.Optional("entry_id"): cv.string,
})
SERVICE_SET_FLOW_SCHEMA = vol.Schema({
    vol.Required("liter_pro_stunde"): vol.All(vol.Coerce(int), vol.Range(min=500, max=5000)),
    vol.Optional("entry_id"): cv.string,
})
SERVICE_EMPTY_SCHEMA = vol.Schema({
    vol.Optional("entry_id"): cv.string,
})


def _get_target_entry(hass: HomeAssistant, call: ServiceCall) -> ConfigEntry:
    """Ermittelt den Ziel-Eintrag. Bei mehreren Anlagen muss entry_id angegeben werden."""
    entries = hass.config_entries.async_entries(DOMAIN)
    loaded = [entry for entry in entries if entry.entry_id in hass.data.get(DOMAIN, {})]

    entry_id = call.data.get("entry_id")
    if entry_id:
        entry = next((e for e in loaded if e.entry_id == entry_id), None)
        if entry is None:
            raise ValueError(f"Unbekannte JUDO i-soft PRO Anlage: {entry_id}")
        return entry

    if len(loaded) == 1:
        return loaded[0]

    raise ValueError(
        "Mehrere JUDO i-soft PRO Anlagen sind eingerichtet. "
        "Bitte bei dem Dienst 'entry_id' der gewünschten Anlage angeben."
    )


def _send_rest_post(entry: ConfigEntry, command: str) -> None:
    """Sendet einen POST. Die globale Ratebegrenzung gilt auch für POST-Kommandos."""
    config = entry.data
    response = request(
        "POST",
        config[CONF_IP_ADDRESS],
        config[CONF_USERNAME],
        config[CONF_PASSWORD],
        command,
        timeout=10,
    )
    _LOGGER.info(
        "JUDO i-soft PRO REST POST %s an %s gesendet. HTTP %s",
        command,
        config[CONF_IP_ADDRESS],
        response.status_code,
    )


async def _register_services(hass: HomeAssistant) -> None:
    """Registriert die globalen Dienste genau einmal."""

    async def run(call: ServiceCall, command_builder):
        entry = _get_target_entry(hass, call)
        command = command_builder(call)
        await hass.async_add_executor_job(_send_rest_post, entry, command)

    async def set_hardness(call):
        await run(call, lambda c: f"3000{c.data['haerte']:02X}")

    async def start_regeneration(call):
        await run(call, lambda c: "350000")

    async def leak_close(call):
        await run(call, lambda c: "3C00")

    async def leak_open(call):
        await run(call, lambda c: "3D00")

    async def activate_scene(call):
        return await run(
            call,
            lambda c: f"3600{c.data['szene']:02X}{c.data['dauer_hex'].upper()}",
        )

    async def start_holiday(call):
        return await run(call, lambda c: f"410001{c.data['tage']:02X}")

    async def set_max_volume(call):
        return await run(
            call,
            lambda c: f"3F00{c.data['liter'] % 256:02X}{c.data['liter'] // 256:02X}",
        )

    async def set_max_flow(call):
        return await run(
            call,
            lambda c: f"4000{c.data['liter_pro_stunde'] % 256:02X}{c.data['liter_pro_stunde'] // 256:02X}",
        )

    hass.services.async_register(DOMAIN, "set_wunschwasserhaerte", set_hardness, schema=SERVICE_SET_HARDNESS_SCHEMA)
    hass.services.async_register(DOMAIN, "start_regeneration", start_regeneration, schema=SERVICE_EMPTY_SCHEMA)
    hass.services.async_register(DOMAIN, "close_leak_protection", leak_close, schema=SERVICE_EMPTY_SCHEMA)
    hass.services.async_register(DOMAIN, "open_leak_protection", leak_open, schema=SERVICE_EMPTY_SCHEMA)
    hass.services.async_register(DOMAIN, "activate_scene", activate_scene, schema=SERVICE_SET_SCENE_SCHEMA)
    hass.services.async_register(DOMAIN, "start_holiday_mode", start_holiday, schema=SERVICE_SET_DAYS_SCHEMA)
    hass.services.async_register(DOMAIN, "set_max_volume", set_max_volume, schema=SERVICE_SET_VOLUME_SCHEMA)
    hass.services.async_register(DOMAIN, "set_max_flow", set_max_flow, schema=SERVICE_SET_FLOW_SCHEMA)

    hass.data[DOMAIN][SERVICES_REGISTERED] = True


async def async_setup(hass: HomeAssistant, config) -> bool:
    """Initialisiert die Integration."""
    hass.data.setdefault(DOMAIN, {})
    if not hass.data[DOMAIN].get(SERVICES_REGISTERED):
        await _register_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Richtet eine JUDO i-soft PRO Anlage ein."""
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entfernt eine Instanz der Integration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok

"""Setup der JUDO i-soft Custom Component und Registrierung der Dienste."""
import logging
import requests
from requests.auth import HTTPBasicAuth
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_IP_ADDRESS, CONF_USERNAME, CONF_PASSWORD

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]

SERVICE_SET_HARDNESS_SCHEMA = vol.Schema({
    vol.Required("haerte"): vol.All(vol.Coerce(int), vol.Range(min=0, max=30)),
})

SERVICE_SET_SCENE_SCHEMA = vol.Schema({
    vol.Required("szene"): vol.All(vol.Coerce(int), vol.Range(min=0, max=10)),
    vol.Required("dauer_hex"): str,
})

SERVICE_SET_DAYS_SCHEMA = vol.Schema({
    vol.Required("tage"): vol.All(vol.Coerce(int), vol.Range(min=1, max=30)),
})

SERVICE_SET_VOLUME_SCHEMA = vol.Schema({
    vol.Required("liter"): vol.All(vol.Coerce(int), vol.Range(min=100, max=3000)),
})

SERVICE_SET_FLOW_SCHEMA = vol.Schema({
    vol.Required("liter_pro_stunde"): vol.All(vol.Coerce(int), vol.Range(min=500, max=5000)),
})

SERVICE_EMPTY_SCHEMA = vol.Schema({})

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Richtet den Eintrag aus dem Config Flow ein."""
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    def send_rest_post(cmd: str):
        ip = entry.data[CONF_IP_ADDRESS]
        user = entry.data[CONF_USERNAME]
        pwd = entry.data[CONF_PASSWORD]
        url = f"http://{ip}/api/rest/{cmd}"
        
        try:
            res = requests.post(url, auth=HTTPBasicAuth(user, pwd), timeout=10)
            _LOGGER.info("REST Command %s gesendet. Status: %s", cmd, res.status_code)
        except Exception as err:
            _LOGGER.error("Fehler beim Senden von REST Command %s: %s", cmd, err)

    # Handler-Funktionen für Dienste
    async def handle_set_wunschwasserhaerte(call: ServiceCall):
        haerte = call.data.get("haerte")
        await hass.async_add_executor_job(send_rest_post, f"3000{haerte:02X}")

    async def handle_start_regeneration(call: ServiceCall):
        await hass.async_add_executor_job(send_rest_post, "350000")

    async def handle_leak_close(call: ServiceCall):
        await hass.async_add_executor_job(send_rest_post, "3C00")

    async def handle_leak_open(call: ServiceCall):
        await hass.async_add_executor_job(send_rest_post, "3D00")

    async def handle_activate_scene(call: ServiceCall):
        szene = call.data.get("szene")
        dauer = call.data.get("dauer_hex").upper()
        await hass.async_add_executor_job(send_rest_post, f"3600{szene:02X}{dauer}")

    async def handle_start_holiday(call: ServiceCall):
        tage = call.data.get("tage")
        await hass.async_add_executor_job(send_rest_post, f"410001{tage:02X}")

    async def handle_set_max_volume(call: ServiceCall):
        liter = call.data.get("liter")
        byte1 = liter % 256
        byte2 = liter // 256
        await hass.async_add_executor_job(send_rest_post, f"3F00{byte1:02X}{byte2:02X}")

    async def handle_set_max_flow(call: ServiceCall):
        l_h = call.data.get("liter_pro_stunde")
        byte1 = l_h % 256
        byte2 = l_h // 256
        await hass.async_add_executor_job(send_rest_post, f"4000{byte1:02X}{byte2:02X}")

    # Registrierung aller Dienste
    hass.services.async_register(DOMAIN, "set_wunschwasserhaerte", handle_set_wunschwasserhaerte, schema=SERVICE_SET_HARDNESS_SCHEMA)
    hass.services.async_register(DOMAIN, "start_regeneration", handle_start_regeneration, schema=SERVICE_EMPTY_SCHEMA)
    hass.services.async_register(DOMAIN, "close_leak_protection", handle_leak_close, schema=SERVICE_EMPTY_SCHEMA)
    hass.services.async_register(DOMAIN, "open_leak_protection", handle_leak_open, schema=SERVICE_EMPTY_SCHEMA)
    hass.services.async_register(DOMAIN, "activate_scene", handle_activate_scene, schema=SERVICE_SET_SCENE_SCHEMA)
    hass.services.async_register(DOMAIN, "start_holiday_mode", handle_start_holiday, schema=SERVICE_SET_DAYS_SCHEMA)
    hass.services.async_register(DOMAIN, "set_max_volume", handle_set_max_volume, schema=SERVICE_SET_VOLUME_SCHEMA)
    hass.services.async_register(DOMAIN, "set_max_flow", handle_set_max_flow, schema=SERVICE_SET_FLOW_SCHEMA)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entfernt eine Instanz der Integration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
"""Select-Plattform für JUDO i-soft PRO Szenenauswahl."""
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import request
from .const import (
    DOMAIN,
    CONF_IP_ADDRESS,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_DEVICE_NAME,
)

_LOGGER = logging.getLogger(__name__)

SCENE_OPTIONS = {
    "Szene 0: Alltag meistern": 0,
    "Szene 1: Körper pflegen": 1,
    "Szene 2: Garten bewässern": 2,
    "Szene 3: Urlaub genießen": 3,
    "Szene 4: Wäsche waschen": 4,
    "Szene 5: Hochdruckreinigen": 5,
    "Szene 6: Pool befüllen": 6,
    "Szene 7: Heizung befüllen": 7,
    "Szene 8: Custom Szene 1": 8,
    "Szene 9: Custom Szene 2": 9,
    "Szene 10: Custom Szene 3": 10,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Erstellt die Szenenauswahl-Entität."""
    config = entry.data
    ip = config[CONF_IP_ADDRESS]
    user = config[CONF_USERNAME]
    pwd = config[CONF_PASSWORD]
    device_name = config.get(CONF_DEVICE_NAME) or f"JUDO i-soft PRO ({ip})"

    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=device_name,
        manufacturer="JUDO",
        model="i-soft PRO / L",
        configuration_url=f"http://{ip}",
    )

    async_add_entities([JudoSceneSelect(entry, device_info, ip, user, pwd)], True)


class JudoSceneSelect(SelectEntity):
    """Szenenauswahl-Dropdown."""

    def __init__(self, entry, device_info, ip, user, pwd):
        self._entry = entry
        self._ip = ip
        self._user = user
        self._pwd = pwd
        self._attr_name = "i-soft PRO Szenenauswahl"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_scene_select"
        self._attr_device_info = device_info
        self._attr_icon = "mdi:palette"
        self._attr_options = list(SCENE_OPTIONS.keys())
        self._attr_current_option = list(SCENE_OPTIONS.keys())[0]

    async def async_select_option(self, option: str) -> None:
        scene_id = SCENE_OPTIONS.get(option, 0)
        
        # Holt die eingestellte Szenendauer aus der Number-Entität (Standard: 2 Std / 02 Hex)
        duration_entity_id = f"number.i_soft_pro_szenendauer_einstellen"
        duration_state = self.hass.states.get(duration_entity_id)
        duration_hours = int(float(duration_state.state)) if duration_state else 2
        
        dauer_hex = f"{duration_hours:02X}00"
        command = f"3600{scene_id:02X}{dauer_hex}"

        try:
            await self.hass.async_add_executor_job(
                request, "POST", self._ip, self._user, self._pwd, command, 10.0
            )
            self._attr_current_option = option
            self.async_write_ha_state()
            _LOGGER.info("Szene '%s' (%s) aktiviert für %d Std.", option, command, duration_hours)
        except Exception as err:
            _LOGGER.error("Fehler beim Aktivieren der Szene %s: %s", option, err)

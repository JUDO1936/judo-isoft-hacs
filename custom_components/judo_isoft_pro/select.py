"""Select-Plattform für JUDO i-soft PRO Szenenauswahl."""
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import request
from .const import (
    CONF_DEVICE_NAME,
    CONF_IP_ADDRESS,
    CONF_PASSWORD,
    CONF_USERNAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

SCENE_MAPPING = {
    "Szene 00 (Alltag meistern)": "00",
    "Szene 01 (Körper pflegen)": "01",
    "Szene 02 (Garten bewässern)": "02",
    "Szene 03 (Urlaub genießen)": "03",
    "Szene 04 (Wäsche waschen)": "04",
    "Szene 05 (Hochdruckreinigen)": "05",
    "Szene 06 (Pool befüllen)": "06",
    "Szene 07 (Heizung befüllen)": "07",
    "Szene 08 (Custom Szene 1)": "08",
    "Szene 09 (Custom Szene 2)": "09",
    "Szene 0A (Custom Szene 3)": "0A",
}

REVERSE_SCENE_MAPPING = {v: k for k, v in SCENE_MAPPING.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Erstellt die Select-Entität."""
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

    async_add_entities([JudoIsoftSceneSelect(entry, device_info, ip, user, pwd)], False)


class JudoIsoftSceneSelect(SelectEntity):
    """Dropdown-Menü zur Szenenauswahl."""

    def __init__(self, entry, device_info, ip, user, pwd):
        self._entry = entry
        self._ip = ip
        self._user = user
        self._pwd = pwd
        self._attr_name = "i-soft PRO Szenenauswahl"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_scene_select"
        self._attr_device_info = device_info
        self._attr_icon = "mdi:playlist-check"
        self._attr_options = list(SCENE_MAPPING.keys())
        self._attr_current_option = self._attr_options[0]

    def select_option(self, option: str) -> None:
        """Aktiviert die gewählte Szene."""
        scene_code = SCENE_MAPPING.get(option)
        if not scene_code:
            return

        command = f"60{scene_code}"
        try:
            response = request("GET", self._ip, self._user, self._pwd, command, timeout=10)
            if response.status_code == 200:
                self._attr_current_option = option
                self.schedule_update_ha_state()
        except Exception as err:
            _LOGGER.error("Fehler beim Setzen der Szene (%s): %s", command, err)

    def update(self) -> None:
        """Liest die aktive Szene aus (Kommando 6900)."""
        try:
            response = request("GET", self._ip, self._user, self._pwd, "6900", timeout=10)
            if response.status_code == 200:
                data = response.json().get("data", "")
                if len(data) >= 4:
                    scene_hex = f"{int(data[2:4], 16):02X}"
                    if scene_hex in REVERSE_SCENE_MAPPING:
                        self._attr_current_option = REVERSE_SCENE_MAPPING[scene_hex]
        except Exception as err:
            _LOGGER.error("Fehler beim Abrufen der aktiven Szene: %s", err)

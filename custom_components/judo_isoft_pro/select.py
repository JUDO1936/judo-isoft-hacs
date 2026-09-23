"""Select-Plattform für JUDO i-soft PRO Dropdown-Einstellungen."""
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

# --- Mappings für Dropdowns ---
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

SCENE_DURATION_MAPPING = {
    "15 Minuten": 15,
    "30 Minuten": 30,
    "45 Minuten": 45,
    "60 Minuten (1 Std)": 60,
    "90 Minuten (1,5 Std)": 90,
    "120 Minuten (2 Std)": 120,
    "180 Minuten (3 Std)": 180,
    "240 Minuten (4 Std)": 240,
    "360 Minuten (6 Std)": 360,
    "720 Minuten (12 Std)": 720,
    "1440 Minuten (24 Std)": 1440,
}
REVERSE_DURATION_MAPPING = {v: k for k, v in SCENE_DURATION_MAPPING.items()}

HARDNESS_UNIT_MAPPING = {
    "°dH": 0,
    "°fH": 1,
    "ppm": 2,
    "mmol/l": 3,
}
REVERSE_HARDNESS_UNIT_MAPPING = {v: k for k, v in HARDNESS_UNIT_MAPPING.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Erstellt alle Dropdown-Steuerelemente."""
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

    async_add_entities(
        [
            JudoIsoftSceneSelect(entry, device_info, ip, user, pwd),
            JudoSceneDurationSelect(entry, device_info, ip, user, pwd),
            JudoHardnessUnitSelect(entry, device_info, ip, user, pwd),
        ],
        False,
    )


class JudoIsoftBaseSelect(SelectEntity):
    """Basisklasse für Select-Entitäten."""

    def __init__(self, entry, device_info, ip, user, pwd):
        self._entry = entry
        self._ip = ip
        self._user = user
        self._pwd = pwd
        self._attr_device_info = device_info

    def _fetch_cmd(self, command: str) -> str | None:
        try:
            response = request("GET", self._ip, self._user, self._pwd, command, timeout=10)
            if response.status_code == 200:
                data = response.json().get("data", "")
                return str(data).strip() if data is not None else None
        except Exception as err:
            _LOGGER.error("Fehler beim Abrufen von Kommando %s von %s: %s", command, self._ip, err)
        return None

    def _send_cmd(self, command: str) -> bool:
        try:
            response = request("GET", self._ip, self._user, self._pwd, command, timeout=10)
            if response.status_code == 200:
                return True
        except Exception as err:
            _LOGGER.error("Fehler beim Senden von Kommando %s an %s: %s", command, self._ip, err)
        return False


class JudoIsoftSceneSelect(JudoIsoftBaseSelect):
    """Dropdown zur Auswahl der Szene."""

    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Szenenauswahl"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_scene_select"
        self._attr_icon = "mdi:playlist-check"
        self._attr_options = list(SCENE_MAPPING.keys())
        self._attr_current_option = self._attr_options[0]

    def select_option(self, option: str) -> None:
        scene_code = SCENE_MAPPING.get(option)
        if not scene_code:
            return

        command = f"60{scene_code}"
        if self._send_cmd(command):
            self._attr_current_option = option
            self.schedule_update_ha_state()

    def update(self) -> None:
        data = self._fetch_cmd("6900")
        if data and len(data) >= 4:
            try:
                scene_hex = f"{int(data[2:4], 16):02X}"
                if scene_hex in REVERSE_SCENE_MAPPING:
                    self._attr_current_option = REVERSE_SCENE_MAPPING[scene_hex]
            except ValueError:
                pass


class JudoSceneDurationSelect(JudoIsoftBaseSelect):
    """Dropdown zur Einstellung der Szenendauer."""

    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Szenendauer"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_scene_duration_select"
        self._attr_icon = "mdi:timer-cog-outline"
        self._attr_options = list(SCENE_DURATION_MAPPING.keys())
        self._attr_current_option = self._attr_options[3]

    def select_option(self, option: str) -> None:
        minutes = SCENE_DURATION_MAPPING.get(option)
        if minutes is None:
            return

        hex_val = minutes.to_bytes(2, byteorder="little").hex().upper()
        command = f"37{hex_val}"
        if self._send_cmd(command):
            self._attr_current_option = option
            self.schedule_update_ha_state()

    def update(self) -> None:
        data = self._fetch_cmd("37")
        if data and len(data) >= 4:
            try:
                minutes = int.from_bytes(bytes.fromhex(data[:4]), byteorder="little")
                if minutes in REVERSE_DURATION_MAPPING:
                    self._attr_current_option = REVERSE_DURATION_MAPPING[minutes]
            except ValueError:
                pass


class JudoHardnessUnitSelect(JudoIsoftBaseSelect):
    """Dropdown zur Auswahl der Härteeinheit (°dH, °fH, ppm, mmol/l)."""

    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Härteeinheit Einstellen"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_hardness_unit_select"
        self._attr_icon = "mdi:atom"
        self._attr_options = list(HARDNESS_UNIT_MAPPING.keys())
        self._attr_current_option = self._attr_options[0]

    def select_option(self, option: str) -> None:
        unit_code = HARDNESS_UNIT_MAPPING.get(option)
        if unit_code is None:
            return

        data = self._fetch_cmd("20")
        current_hardness = 8
        if data and len(data) >= 2:
            try:
                current_hardness = int(data[:2], 16)
            except ValueError:
                pass

        command = f"20{current_hardness:02X}{unit_code:02X}"
        if self._send_cmd(command):
            self._attr_current_option = option
            self.schedule_update_ha_state()

    def update(self) -> None:
        data = self._fetch_cmd("20")
        if data and len(data) >= 4:
            try:
                unit_code = int(data[2:4], 16)
                if unit_code in REVERSE_HARDNESS_UNIT_MAPPING:
                    self._attr_current_option = REVERSE_HARDNESS_UNIT_MAPPING[unit_code]
            except ValueError:
                pass

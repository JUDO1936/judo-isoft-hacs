"""Switch-Plattform für JUDO i-soft PRO Leckageschutz."""
import logging

from homeassistant.components.switch import SwitchEntity
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


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Erstellt den Schalter für den Leckageschutz."""
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

    async_add_entities([JudoIsoftLeakageSwitch(entry, device_info, ip, user, pwd)], False)


class JudoIsoftLeakageSwitch(SwitchEntity):
    """Schalter für das Hauptventil / Leckageschutz."""

    def __init__(self, entry, device_info, ip, user, pwd):
        self._entry = entry
        self._ip = ip
        self._user = user
        self._pwd = pwd
        self._attr_name = "i-soft PRO Leckageschutz"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_leakage_switch"
        self._attr_device_info = device_info
        self._attr_icon = "mdi:shield-check"
        self._is_on = False

    @property
    def is_on(self) -> bool:
        return self._is_on

    def turn_on(self, **kwargs) -> None:
        """Schließt das Ventil (Kommando 3C00)."""
        self._send_command("3C00", True)

    def turn_off(self, **kwargs) -> None:
        """Öffnet das Ventil (Kommando 3D00)."""
        self._send_command("3D00", False)

    def _send_command(self, command: str, target_state: bool) -> None:
        try:
            response = request("GET", self._ip, self._user, self._pwd, command, timeout=10)
            if response.status_code == 200:
                self._is_on = target_state
                self.schedule_update_ha_state()
        except Exception as err:
            _LOGGER.error("Fehler beim Schalten (%s): %s", command, err)

    def update(self) -> None:
        """Liest den Ventil-Status über 6900 (Byte 2) aus."""
        try:
            response = request("GET", self._ip, self._user, self._pwd, "6900", timeout=10)
            if response.status_code == 200:
                data = response.json().get("data", "")
                if len(data) >= 6:
                    status_byte = int(data[4:6], 16)
                    self._is_on = (status_byte == 0x07)
        except Exception as err:
            _LOGGER.error("Fehler beim Statusabruf des Leckageschutzes: %s", err)

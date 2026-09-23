"""Switch-Plattform für JUDO i-soft PRO / L Leckageschutz."""
import logging

from homeassistant.components.switch import SwitchEntity
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


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Erstellt den Schalter für den Leckageschutz einer JUDO i-soft PRO Anlage."""
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

    async_add_entities([JudoIsoftLeakageSwitch(entry, device_info, ip, user, pwd)], True)


class JudoIsoftLeakageSwitch(SwitchEntity):
    """Repräsentiert den Schalter zur Steuerung des Leckageschutzes (Absperrventil)."""

    def __init__(self, entry: ConfigEntry, device_info: DeviceInfo, ip: str, user: str, pwd: str) -> None:
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
        """Gibt zurück, ob der Leckageschutz/das Ventil aktiv ist."""
        return self._is_on

    def turn_on(self, **kwargs) -> None:
        """Schließt den Leckageschutz / sperrt die Wasserleitung ab (Kommando 3C00)."""
        self._send_command("3C00", True)

    def turn_off(self, **kwargs) -> None:
        """Öffnet den Leckageschutz / gibt die Wasserleitung frei (Kommando 3D00)."""
        self._send_command("3D00", False)

    def _send_command(self, command: str, target_state: bool) -> None:
        try:
            response = request(
                "GET",
                self._ip,
                self._user,
                self._pwd,
                command,
                timeout=10,
            )

            if response.status_code == 200:
                self._is_on = target_state
                self.schedule_update_ha_state()
                _LOGGER.info("JUDO i-soft PRO %s: Leckageschutz-Kommando %s erfolgreich gesendet", self._ip, command)
            else:
                _LOGGER.warning("JUDO i-soft PRO %s: REST %s liefert HTTP %s", self._ip, command, response.status_code)
        except Exception as err:
            _LOGGER.error("Fehler beim Schalten des Leckageschutzes an JUDO i-soft PRO %s / %s: %s", self._ip, command, err)

    def update(self) -> None:
        """Liest den aktuellen Status des Leckageschutzes über Kommando 6900 aus."""
        try:
            response = request(
                "GET",
                self._ip,
                self._user,
                self._pwd,
                "6900",
                timeout=10,
            )

            if response.status_code != 200:
                _LOGGER.warning("JUDO i-soft PRO %s: REST 6900 liefert HTTP %s", self._ip, response.status_code)
                return

            data = response.json().get("data", "")
            if len(data) >= 26:
                # Byte 2 (Index 4:6 in Hex-String) = 0x07 entspricht "Leckageschutz aktiv"
                status_byte = int(data[4:6], 16)
                self._is_on = (status_byte == 0x07)

        except Exception as err:
            _LOGGER.error("Fehler beim Abrufen des Leckageschutz-Status von JUDO i-soft PRO %s / 6900: %s", self._ip, err)

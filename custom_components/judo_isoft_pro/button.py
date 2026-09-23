"""Button-Plattform für JUDO i-soft PRO / L."""
import logging

from homeassistant.components.button import ButtonEntity
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
    """Erstellt alle Button-Entitäten für eine JUDO i-soft PRO Anlage."""
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

    buttons = [
        JudoRegenerationButton(entry, device_info, ip, user, pwd),
        JudoLeakCloseButton(entry, device_info, ip, user, pwd),
        JudoLeakOpenButton(entry, device_info, ip, user, pwd),
    ]

    async_add_entities(buttons, True)


class JudoBaseButton(ButtonEntity):
    """Basisklasse für JUDO Button-Entitäten."""

    def __init__(self, entry, device_info, ip, user, pwd, name, unique_key, command, icon):
        self._entry = entry
        self._ip = ip
        self._user = user
        self._pwd = pwd
        self._command = command
        self._attr_name = f"i-soft PRO {name}"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_{unique_key}"
        self._attr_device_info = device_info
        self._attr_icon = icon

    async def async_press(self) -> None:
        """Führt das REST-POST-Kommando aus."""
        try:
            await self.hass.async_add_executor_job(
                request, "POST", self._ip, self._user, self._pwd, self._command, 10.0
            )
            _LOGGER.info("Button '%s' erfolgreich ausgeführt.", self._attr_name)
        except Exception as err:
            _LOGGER.error("Fehler beim Ausführen von '%s': %s", self._attr_name, err)


class JudoRegenerationButton(JudoBaseButton):
    """Button zum Auslösen einer manuellen Regeneration."""

    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(
            entry, device_info, ip, user, pwd,
            name="Regeneration Starten",
            unique_key="start_regeneration",
            command="350000",
            icon="mdi:sync",
        )


class JudoLeakCloseButton(JudoBaseButton):
    """Button zum Schließen des Leckageschutz-Ventils."""

    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(
            entry, device_info, ip, user, pwd,
            name="Leckageschutz Schließen",
            unique_key="close_leak_protection",
            command="3C00",
            icon="mdi:valve-closed",
        )


class JudoLeakOpenButton(JudoBaseButton):
    """Button zum Öffnen des Leckageschutz-Ventils."""

    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(
            entry, device_info, ip, user, pwd,
            name="Leckageschutz Öffnen",
            unique_key="open_leak_protection",
            command="3D00",
            icon="mdi:valve-open",
        )

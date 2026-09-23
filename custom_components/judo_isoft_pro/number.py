"""Number-Plattform für JUDO i-soft PRO Steuerungseinstellungen."""
import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfTime,
    UnitOfVolume,
)
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
    """Erstellt alle Number-Steuerelemente für die JUDO i-soft PRO."""
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
            JudoSaltWarningThresholdNumber(entry, device_info, ip, user, pwd),
            JudoSceneDurationNumber(entry, device_info, ip, user, pwd),
            JudoTargetHardnessNumber(entry, device_info, ip, user, pwd),
            JudoMaxEntnahmedauerNumber(entry, device_info, ip, user, pwd),
            JudoMaxEntnahmemengeNumber(entry, device_info, ip, user, pwd),
            JudoMaxVolumenstromNumber(entry, device_info, ip, user, pwd),
        ],
        False,
    )


class JudoIsoftBaseNumber(NumberEntity):
    """Basisklasse für Number-Entitäten."""

    def __init__(self, entry, device_info, ip, user, pwd) -> None:
        self._entry = entry
        self._ip = ip
        self._user = user
        self._pwd = pwd
        self._attr_device_info = device_info
        self._attr_mode = NumberMode.BOX

    def _send_cmd(self, command: str) -> bool:
        try:
            response = request("GET", self._ip, self._user, self._pwd, command, timeout=10)
            if response.status_code == 200:
                return True
        except Exception as err:
            _LOGGER.error("Fehler beim Senden von Kommando %s an %s: %s", command, self._ip, err)
        return False

    def _fetch_cmd(self, command: str) -> str | None:
        try:
            response = request("GET", self._ip, self._user, self._pwd, command, timeout=10)
            if response.status_code == 200:
                return response.json().get("data", "")
        except Exception as err:
            _LOGGER.error("Fehler beim Abrufen von Kommando %s von %s: %s", command, self._ip, err)
        return None


class JudoSaltWarningThresholdNumber(JudoIsoftBaseNumber):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Salzmangel Warnschwelle Einstellen"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_salt_warning_threshold_set"
        self._attr_native_min_value = 1
        self._attr_native_max_value = 90
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = UnitOfTime.DAYS
        self._attr_icon = "mdi:alert-plus-outline"

    def set_native_value(self, value: float) -> None:
        days = int(value)
        hex_val = days.to_bytes(2, byteorder="little").hex().upper()
        if self._send_cmd(f"94{hex_val}"):
            self._attr_native_value = days
            self.schedule_update_ha_state()

    def update(self) -> None:
        data = self._fetch_cmd("94")
        if data and len(data) >= 12:
            self._attr_native_value = int.from_bytes(bytes.fromhex(data[8:12]), byteorder="little")


class JudoSceneDurationNumber(JudoIsoftBaseNumber):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Szenendauer Einstellen"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_scene_duration_set"
        self._attr_native_min_value = 5
        self._attr_native_max_value = 1440
        self._attr_native_step = 5
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        self._attr_icon = "mdi:timer-cog-outline"

    def set_native_value(self, value: float) -> None:
        minutes = int(value)
        hex_val = minutes.to_bytes(2, byteorder="little").hex().upper()
        if self._send_cmd(f"37{hex_val}"):
            self._attr_native_value = minutes
            self.schedule_update_ha_state()

    def update(self) -> None:
        data = self._fetch_cmd("37")
        if data and len(data) >= 4:
            self._attr_native_value = int.from_bytes(bytes.fromhex(data[:4]), byteorder="little")


class JudoTargetHardnessNumber(JudoIsoftBaseNumber):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Wunschwasserhärte Einstellen"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_target_hardness_set"
        self._attr_native_min_value = 1
        self._attr_native_max_value = 20
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "°dH"
        self._attr_icon = "mdi:water-plus-outline"

    def set_native_value(self, value: float) -> None:
        hardness = int(value)
        if self._send_cmd(f"20{hardness:02X}"):
            self._attr_native_value = hardness
            self.schedule_update_ha_state()

    def update(self) -> None:
        data = self._fetch_cmd("20")
        if data and len(data) >= 2:
            self._attr_native_value = int(data[:2], 16)


class JudoMaxEntnahmedauerNumber(JudoIsoftBaseNumber):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Max. Entnahmedauer Einstellen"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_max_entnahmedauer_set"
        self._attr_native_min_value = 10
        self._attr_native_max_value = 600
        self._attr_native_step = 10
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        self._attr_icon = "mdi:clock-edit-outline"

    def set_native_value(self, value: float) -> None:
        minutes = int(value)
        hex_val = minutes.to_bytes(2, byteorder="little").hex().upper()
        if self._send_cmd(f"3B01{hex_val}"):
            self._attr_native_value = minutes
            self.schedule_update_ha_state()

    def update(self) -> None:
        data = self._fetch_cmd("3B")
        if data and len(data) >= 4:
            self._attr_native_value = int.from_bytes(bytes.fromhex(data[:4]), byteorder="little")


class JudoMaxEntnahmemengeNumber(JudoIsoftBaseNumber):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Max. Entnahmemenge Einstellen"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_max_entnahmemenge_set"
        self._attr_native_min_value = 50
        self._attr_native_max_value = 5000
        self._attr_native_step = 50
        self._attr_native_unit_of_measurement = UnitOfVolume.LITERS
        self._attr_icon = "mdi:water-minus-outline"

    def set_native_value(self, value: float) -> None:
        liters = int(value)
        hex_val = liters.to_bytes(2, byteorder="little").hex().upper()
        if self._send_cmd(f"3B02{hex_val}"):
            self._attr_native_value = liters
            self.schedule_update_ha_state()

    def update(self) -> None:
        data = self._fetch_cmd("3B")
        if data and len(data) >= 8:
            self._attr_native_value = int.from_bytes(bytes.fromhex(data[4:8]), byteorder="little")


class JudoMaxVolumenstromNumber(JudoIsoftBaseNumber):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Max. Volumenstrom Einstellen"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_max_volumenstrom_set"
        self._attr_native_min_value = 500
        self._attr_native_max_value = 5000
        self._attr_native_step = 100
        self._attr_native_unit_of_measurement = "L/h"
        self._attr_icon = "mdi:speedometer-medium"

    def set_native_value(self, value: float) -> None:
        flow = int(value)
        hex_val = flow.to_bytes(2, byteorder="little").hex().upper()
        if self._send_cmd(f"3B03{hex_val}"):
            self._attr_native_value = flow
            self.schedule_update_ha_state()

    def update(self) -> None:
        data = self._fetch_cmd("3B")
        if data and len(data) >= 12:
            self._attr_native_value = int.from_bytes(bytes.fromhex(data[8:12]), byteorder="little")

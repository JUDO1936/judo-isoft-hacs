"""Sensor-Plattform für JUDO i-soft PRO / L Status und Messwerte."""
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfVolume
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

# Zuordnung des Leckagegrundes (Byte 3 / Index 6:8)
LEAKAGE_REASON_MAPPING = {
    0: "Keine Warnung / Normalbetrieb",
    1: "Maximalzeit überschritten",
    2: "Maximalmenge überschritten",
    3: "Maximaldurchfluss überschritten",
    4: "Mikroleckage erkannt",
    5: "Bodendatensensor ausgelöst",
    6: "Manuell abgesperrt",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Erstellt die Sensoren für eine konfigurierte JUDO i-soft PRO Anlage."""
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
            JudoFlowRateSensor(entry, device_info, ip, user, pwd),
            JudoTotalVolumeSensor(entry, device_info, ip, user, pwd),
            JudoWaterTempSensor(entry, device_info, ip, user, pwd),
            JudoLeakageReasonSensor(entry, device_info, ip, user, pwd),
        ],
        True,
    )


class JudoIsoftBaseSensor(SensorEntity):
    """Basisklasse für JUDO i-soft PRO Sensoren."""

    def __init__(
        self, entry: ConfigEntry, device_info: DeviceInfo, ip: str, user: str, pwd: str
    ) -> None:
        self._entry = entry
        self._ip = ip
        self._user = user
        self._pwd = pwd
        self._attr_device_info = device_info

    def _get_6900_data(self) -> str | None:
        """Ruft den 16-Byte Hex-Payload des Kommandos 6900 ab."""
        try:
            response = request("GET", self._ip, self._user, self._pwd, "6900", timeout=10)
            if response.status_code == 200:
                return response.json().get("data", "")
            _LOGGER.warning("JUDO i-soft PRO %s: REST 6900 liefert HTTP %s", self._ip, response.status_code)
        except Exception as err:
            _LOGGER.error("Fehler beim Abrufen der Statusdaten von %s / 6900: %s", self._ip, err)
        return None


class JudoFlowRateSensor(JudoIsoftBaseSensor):
    """Sensor für den aktuellen Wasserdurchfluss in L/h."""

    def __init__(self, entry: ConfigEntry, device_info: DeviceInfo, ip: str, user: str, pwd: str) -> None:
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Durchfluss"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_flow_rate"
        self._attr_native_unit_of_measurement = "L/h"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:water-pump"

    def update(self) -> None:
        data = self._get_6900_data()
        if data and len(data) >= 26:
            # Byte 4-5 (Index 8:12 in Hex-String), Little-Endian
            flow_bytes = bytes.fromhex(data[8:12])
            self._attr_native_value = int.from_bytes(flow_bytes, byteorder="little")


class JudoTotalVolumeSensor(JudoIsoftBaseSensor):
    """Sensor für den Gesamtwasserverbrauch in m³."""

    def __init__(self, entry: ConfigEntry, device_info: DeviceInfo, ip: str, user: str, pwd: str) -> None:
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Wasserverbrauch Gesamt"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_total_volume"
        self._attr_device_class = SensorDeviceClass.WATER
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS

    def update(self) -> None:
        data = self._get_6900_data()
        if data and len(data) >= 26:
            # Byte 6-9 (Index 12:20 in Hex-String), Little-Endian, Wert in Litern -> umgerechnet in m³
            vol_bytes = bytes.fromhex(data[12:20])
            liters = int.from_bytes(vol_bytes, byteorder="little")
            self._attr_native_value = round(liters / 1000.0, 3)


class JudoWaterTempSensor(JudoIsoftBaseSensor):
    """Sensor für die Wassertemperatur in °C."""

    def __init__(self, entry: ConfigEntry, device_info: DeviceInfo, ip: str, user: str, pwd: str) -> None:
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Wassertemperatur"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_water_temp"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def update(self) -> None:
        data = self._get_6900_data()
        if data and len(data) >= 26:
            # Byte 10 (Index 20:22 in Hex-String)
            self._attr_native_value = int(data[20:22], 16)


class JudoLeakageReasonSensor(JudoIsoftBaseSensor):
    """Sensor für den aktuellen Leckagestatus / Leckagegrund."""

    def __init__(self, entry: ConfigEntry, device_info: DeviceInfo, ip: str, user: str, pwd: str) -> None:
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Leckagestatus"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_leakage_reason"
        self._attr_icon = "mdi:alert-circle-outline"

    def update(self) -> None:
        data = self._get_6900_data()
        if data and len(data) >= 26:
            # Byte 3 (Index 6:8 in Hex-String)
            reason_code = int(data[6:8], 16)
            self._attr_native_value = LEAKAGE_REASON_MAPPING.get(
                reason_code, f"Unbekannter Status (0x{reason_code:02X})"
            )

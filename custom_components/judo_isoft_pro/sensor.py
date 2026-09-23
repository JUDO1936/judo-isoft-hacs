"""Sensor-Plattform für JUDO i-soft PRO / L."""
import logging

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
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

LEAKAGE_REASONS = {
    0x00: "Keine Leckage",
    0x01: "Volumenstrom überschritten",
    0x02: "Menge überschritten",
    0x04: "Zeit überschritten",
    0x08: "Ext. Kabelsensor",
    0x10: "Manuell geschlossen",
    0x20: "Manuelle Mikroleckage",
    0x40: "Automatische Mikroleckage",
    0x80: "Homeguard Meldung",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Erstellt alle Sensoren für eine konfigurierte JUDO i-soft PRO Anlage."""
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

    sensors = [
        # Standard-Sensoren
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Wunschwasserhärte", "5100", "°dH", "mdi:water-softener", "wunschwasserhaerte"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Salzmangel Warnschwelle", "5700", "Tage", "mdi:alert-circle-outline", "salzmangel_warnschwelle"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Max Entnahmedauer", "3E00", "min", "mdi:timer-outline", "max_entnahmedauer"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Max Entnahmemenge", "3F00", "m³", "mdi:water-minus", "max_entnahmemenge", parse_type="volume"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Max Volumenstrom", "4000", "L/h", "mdi:speedometer", "max_volumenstrom"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Salzgewicht", "5600", "kg", "mdi:salt-shaker", "salzgewicht", parse_type="weight"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Salzreichweite", "5600", "Tage", "mdi:calendar-clock", "salzreichweite", parse_type="salt_range"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Gesamtwassermenge", "2800", "m³", "mdi:water-pump", "gesamtwassermenge", parse_type="volume"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Weichwassermenge", "2900", "m³", "mdi:water-check", "weichwassermenge", parse_type="volume"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Firmware Version", "0100", None, "mdi:file-code-outline", "firmware_version", parse_type="firmware"),
        
        # Sensoren aus Kommando 6900 (Status & Leckageschutz)
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Aktive Szene", "6900", None, "mdi:palette", "aktive_szene", parse_type="6900_scene"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Aktive Szenenoptionen", "6900", None, "mdi:tune", "aktive_szenenoptionen", parse_type="6900_options"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Leckageschutz Status", "6900", None, "mdi:shield-check", "leckageschutz_status", parse_type="6900_leak_status"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Leckagegrund", "6900", None, "mdi:alert-circle-outline", "leckagegrund", parse_type="6900_leak_reason"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Aktueller Durchfluss", "6900", "L/h", "mdi:water-gauge", "aktueller_durchfluss", parse_type="6900_flow"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Aktuelle Durchflussdauer", "6900", "min", "mdi:timer-outline", "aktuelle_durchflussdauer", parse_type="6900_duration"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Aktuelle Wassermenge", "6900", "L", "mdi:water", "aktuelle_wassermenge", parse_type="6900_volume"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Aktuelle Wassertemperatur", "6900", "°C", "mdi:thermometer", "aktuelle_wassertemperatur", parse_type="6900_temp"),
    ]

    async_add_entities(sensors, True)


class JudoIsoftSensor(SensorEntity):
    """Repräsentiert einen JUDO i-soft PRO REST-Sensor."""

    def __init__(self, entry, device_info, ip, user, pwd, name, command, unit, icon, unique_key, parse_type="standard"):
        self._entry = entry
        self._ip = ip
        self._user = user
        self._pwd = pwd
        self._attr_name = f"i-soft PRO {name}"
        self._command = command
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_{unique_key}"
        self._attr_device_info = device_info
        self._parse_type = parse_type
        self._state = None

        if parse_type == "volume":
            self._attr_device_class = SensorDeviceClass.WATER
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        elif parse_type == "6900_temp":
            self._attr_device_class = SensorDeviceClass.TEMPERATURE

    @property
    def native_value(self):
        return self._state

    def update(self) -> None:
        try:
            response = request(
                "GET",
                self._ip,
                self._user,
                self._pwd,
                self._command,
                timeout=10,
            )

            if response.status_code != 200:
                _LOGGER.warning("JUDO i-soft PRO %s: REST %s liefert HTTP %s", self._ip, self._command, response.status_code)
                return

            data = response.json().get("data", "")
            if not data:
                return

            # Standard-Parsing
            if self._parse_type == "weight" and len(data) >= 8:
                weight_g = int(data[2:4] + data[0:2], 16)
                self._state = round(weight_g / 1000, 2)
            elif self._parse_type == "salt_range" and len(data) >= 8:
                self._state = int(data[6:8] + data[4:6], 16)
            elif self._parse_type == "volume" and len(data) >= 8:
                liters = int(data[6:8] + data[4:6] + data[2:4] + data[0:2], 16) if len(data) >= 8 else int(data[2:4] + data[0:2], 16)
                self._state = round(liters / 1000, 3)
            elif self._parse_type == "long_int" and len(data) >= 8:
                self._state = int(data[6:8] + data[4:6] + data[2:4] + data[0:2], 16)
            elif self._parse_type == "firmware" and len(data) >= 6:
                self._state = f"{int(data[4:6], 16)}.{int(data[2:4], 16)}.{int(data[0:2], 16)}"
                
            # Parsing für Kommando 6900 (16-Byte Payload)
            elif self._parse_type == "6900_scene" and len(data) >= 26:
                self._state = f"Szene {int(data[2:4], 16):02X}"
            elif self._parse_type == "6900_options" and len(data) >= 26:
                self._state = f"0x{int(data[4:6], 16):02X}"
            elif self._parse_type == "6900_leak_status" and len(data) >= 26:
                self._state = "Aktiv" if int(data[6:8], 16) == 0x07 else "Deaktiviert"
            elif self._parse_type == "6900_leak_reason" and len(data) >= 26:
                reason_code = int(data[8:10], 16)
                self._state = LEAKAGE_REASONS.get(reason_code, f"Unbekannt (0x{reason_code:02X})")
            elif self._parse_type == "6900_flow" and len(data) >= 26:
                self._state = int(data[12:14] + data[10:12], 16)
            elif self._parse_type == "6900_duration" and len(data) >= 26:
                self._state = int(data[16:18] + data[14:16], 16)
            elif self._parse_type == "6900_volume" and len(data) >= 26:
                self._state = int(data[20:22] + data[18:20], 16)
            elif self._parse_type == "6900_temp" and len(data) >= 26:
                self._state = int(data[24:26] + data[22:24], 16)
                
            elif len(data) >= 4:
                self._state = int(data[2:4] + data[0:2], 16)
            else:
                self._state = int(data[0:2], 16)

        except Exception as err:
            _LOGGER.error("Fehler beim Abrufen von JUDO i-soft PRO %s / %s: %s", self._ip, self._command, err)

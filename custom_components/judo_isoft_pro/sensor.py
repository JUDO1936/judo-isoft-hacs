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
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Wunschwasserhärte", "5100", "°dH", "mdi:water-softener", "wunschwasserhaerte"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Salzmangel Warnschwelle", "5700", "Tage", "mdi:alert-circle-outline", "salzmangel_warnschwelle"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Max Entnahmedauer", "3E00", "min", "mdi:timer-outline", "max_entnahmedauer"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Max Entnahmemenge", "3F00", "L", "mdi:water-minus", "max_entnahmemenge"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Max Volumenstrom", "4000", "L/h", "mdi:speedometer", "max_volumenstrom"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Salzgewicht", "5600", "kg", "mdi:salt-shaker", "salzgewicht", parse_type="weight"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Salzreichweite", "5600", "Tage", "mdi:calendar-clock", "salzreichweite", parse_type="salt_range"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Gesamtwassermenge", "2800", "m³", "mdi:water-pump", "gesamtwassermenge", parse_type="volume"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Weichwassermenge", "2900", "m³", "mdi:water-check", "weichwassermenge", parse_type="volume"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Gerätenummer", "0600", None, "mdi:identifier", "geraetenummer", parse_type="long_int"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Firmware Version", "0100", None, "mdi:file-code-outline", "firmware_version", parse_type="firmware"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Wasserverbrauch Tag", "FB00", "L", "mdi:chart-bar", "wasser_tag", parse_type="long_int"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Wasserverbrauch Monat", "FD00", "L", "mdi:chart-bar", "wasser_monat", parse_type="long_int"),
        JudoIsoftSensor(entry, device_info, ip, user, pwd, "Salzverbrauch Tag", "F300", "g", "mdi:chart-line", "salz_tag"),
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

    @property
    def native_value(self):
        """Gibt den letzten erfolgreich gelesenen Wert zurück."""
        return self._state

    def update(self) -> None:
        """Liest einen Wert; bei Fehler bleibt der letzte Wert erhalten."""
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
                _LOGGER.warning(
                    "JUDO i-soft PRO %s: REST %s liefert HTTP %s",
                    self._ip,
                    self._command,
                    response.status_code,
                )
                return

            data = response.json().get("data", "")
            if not data:
                _LOGGER.warning(
                    "JUDO i-soft PRO %s: REST %s liefert keine Daten",
                    self._ip,
                    self._command,
                )
                return

            if self._parse_type == "weight" and len(data) >= 8:
                weight_g = int(data[2:4] + data[0:2], 16)
                self._state = round(weight_g / 1000, 2)
            elif self._parse_type == "salt_range" and len(data) >= 8:
                self._state = int(data[6:8] + data[4:6], 16)
            elif self._parse_type == "volume" and len(data) >= 8:
                liters = int(data[6:8] + data[4:6] + data[2:4] + data[0:2], 16)
                self._state = round(liters / 1000, 3)
            elif self._parse_type == "long_int" and len(data) >= 8:
                self._state = int(data[6:8] + data[4:6] + data[2:4] + data[0:2], 16)
            elif self._parse_type == "firmware" and len(data) >= 6:
                self._state = f"{int(data[4:6], 16)}.{int(data[2:4], 16)}.{int(data[0:2], 16)}"
            elif len(data) >= 4:
                self._state = int(data[2:4] + data[0:2], 16)
            else:
                self._state = int(data[0:2], 16)

        except Exception as err:
            # Wichtig: _state wird absichtlich NICHT gelöscht.
            _LOGGER.error(
                "Fehler beim Abrufen von JUDO i-soft PRO %s / %s: %s",
                self._ip,
                self._command,
                err,
            )

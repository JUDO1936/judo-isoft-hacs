"""Sensor-Plattform für JUDO i-soft mit zentralem Polling-Schutz."""
import asyncio
from datetime import timedelta
import logging
import requests
from requests.auth import HTTPBasicAuth

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_IP_ADDRESS, CONF_USERNAME, CONF_PASSWORD

_LOGGER = logging.getLogger(__name__)

# Ein globaler Lock sorgt dafür, dass NIEMALS zwei Anfragen gleichzeitig laufen (anlagenübergreifend)
REQUEST_LOCK = asyncio.Lock()

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Erstellt alle Sensoren basierend auf den eingegebenen Zugangsdaten."""
    config = entry.data
    ip = config[CONF_IP_ADDRESS]
    user = config[CONF_USERNAME]
    pwd = config[CONF_PASSWORD]

    sensors = [
        # Einstellungen & Grenzwerte
        JudoIsoftSensor(ip, user, pwd, "Wunschwasserhärte", "5100", "°dH", "mdi:water-softener", "wunschwasserhaerte"),
        JudoIsoftSensor(ip, user, pwd, "Salzmangel Warnschwelle", "5700", "Tage", "mdi:alert-circle-outline", "salzmangel_warnschwelle"),
        JudoIsoftSensor(ip, user, pwd, "Max Entnahmedauer", "3E00", "min", "mdi:timer-outline", "max_entnahmedauer"),
        JudoIsoftSensor(ip, user, pwd, "Max Entnahmemenge", "3F00", "L", "mdi:water-minus", "max_entnahmemenge"),
        JudoIsoftSensor(ip, user, pwd, "Max Volumenstrom", "4000", "L/h", "mdi:speedometer", "max_volumenstrom"),

        # Salz & Verbrauch
        JudoIsoftSensor(ip, user, pwd, "Salzgewicht", "5600", "kg", "mdi:salt-shaker", "salzgewicht", parse_type="weight"),
        JudoIsoftSensor(ip, user, pwd, "Salzreichweite", "5600", "Tage", "mdi:calendar-clock", "salzreichweite", parse_type="salt_range"),
        JudoIsoftSensor(ip, user, pwd, "Gesamtwassermenge", "2800", "m³", "mdi:water-pump", "gesamtwassermenge", parse_type="volume"),
        JudoIsoftSensor(ip, user, pwd, "Weichwassermenge", "2900", "m³", "mdi:water-check", "weichwassermenge", parse_type="volume"),

        # Infodaten
        JudoIsoftSensor(ip, user, pwd, "Gerätenummer", "0600", None, "mdi:identifier", "geraetenummer", parse_type="long_int"),
        JudoIsoftSensor(ip, user, pwd, "Firmware Version", "0100", None, "mdi:file-code-outline", "firmware_version", parse_type="firmware"),
        
        # Statistiken
        JudoIsoftSensor(ip, user, pwd, "Wasserverbrauch Tag", "FB00", "L", "mdi:chart-bar", "wasser_tag", parse_type="long_int"),
        JudoIsoftSensor(ip, user, pwd, "Wasserverbrauch Monat", "FD00", "L", "mdi:chart-bar", "wasser_monat", parse_type="long_int"),
        JudoIsoftSensor(ip, user, pwd, "Salzverbrauch Tag", "F300", "g", "mdi:chart-line", "salz_tag"),
    ]

    # WICHTIG: Hier False übergeben, damit nicht alle 52 Sensoren beim Start auf einmal feuern
    async_add_entities(sensors, False)

class JudoIsoftSensor(SensorEntity):
    """Repräsentiert einen JUDO i-soft REST-Sensor mit Drosselung."""

    def __init__(self, ip, user, pwd, name, command, unit, icon, unique_key, parse_type="standard"):
        self._ip = ip
        self._user = user
        self._pwd = pwd
        self._attr_name = f"i-soft {name}"
        self._command = command
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_unique_id = f"judo_isoft_{ip}_{unique_key}"
        self._parse_type = parse_type
        self._state = None

        if parse_type == "volume":
            self._attr_device_class = SensorDeviceClass.WATER
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self):
        return self._state

    async def async_update(self) -> None:
        """Ruft die Daten thread-sicher und mit mindestens 2s Pause ab."""
        async with REQUEST_LOCK:
            # 1. Führe den HTTP-Request in einem Executor-Thread aus
            await self.hass.async_add_executor_job(self._fetch_data)
            # 2. Erzwinge exakt 2 Sekunden Pause vor der NÄCHSTEN Abfrage
            await asyncio.sleep(2)

    def _fetch_data(self) -> None:
        """Klassischer Request an die REST API."""
        url = f"http://{self._ip}/api/rest/{self._command}"
        try:
            response = requests.get(url, auth=HTTPBasicAuth(self._user, self._pwd), timeout=10)
            if response.status_code == 200:
                data = response.json().get("data", "")
                if data:
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
            _LOGGER.error("Fehler beim Abrufen von %s: %s", url, err)

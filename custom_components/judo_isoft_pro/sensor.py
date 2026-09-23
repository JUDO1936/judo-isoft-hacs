"""Sensor-Plattform für JUDO i-soft PRO / L – Gesamte Sensorik."""
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfMass,
    UnitOfTemperature,
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

LEAKAGE_REASON_MAPPING = {
    0: "Keine Warnung / Normalbetrieb",
    1: "Maximalzeit überschritten",
    2: "Maximalmenge überschritten",
    3: "Maximaldurchfluss überschritten",
    4: "Mikroleckage erkannt",
    5: "Bodendatensensor ausgelöst",
    6: "Manuell abgesperrt",
}

HARDNESS_UNIT_MAPPING = {
    0: "°dH",
    1: "°fH",
    2: "ppm",
    3: "mmol/l",
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

    async_add_entities(
        [
            JudoFlowRateSensor(entry, device_info, ip, user, pwd),
            JudoTotalVolume6900Sensor(entry, device_info, ip, user, pwd),
            JudoWaterTempSensor(entry, device_info, ip, user, pwd),
            JudoLeakageReasonSensor(entry, device_info, ip, user, pwd),
            JudoDeviceStatusSensor(entry, device_info, ip, user, pwd),
            JudoDeviceTypeSensor(entry, device_info, ip, user, pwd),
            JudoFirmwareVersionSensor(entry, device_info, ip, user, pwd),
            JudoTargetHardnessSensor(entry, device_info, ip, user, pwd),
            JudoHardnessUnitSensor(entry, device_info, ip, user, pwd),
            JudoMaxEntnahmedauerSensor(entry, device_info, ip, user, pwd),
            JudoMaxEntnahmemengeSensor(entry, device_info, ip, user, pwd),
            JudoMaxVolumenstromSensor(entry, device_info, ip, user, pwd),
            JudoSaltWeightSensor(entry, device_info, ip, user, pwd),
            JudoSaltRangeSensor(entry, device_info, ip, user, pwd),
            JudoSaltWarningThresholdSensor(entry, device_info, ip, user, pwd),
            JudoTotalVolumeSensor(entry, device_info, ip, user, pwd),
            JudoSoftWaterVolumeSensor(entry, device_info, ip, user, pwd),
        ],
        False,
    )


class JudoIsoftBaseSensor(SensorEntity):
    """Basisklasse mit Hilfsmethoden für REST-Abfragen an die Anlage."""

    def __init__(self, entry: ConfigEntry, device_info: DeviceInfo, ip: str, user: str, pwd: str) -> None:
        self._entry = entry
        self._ip = ip
        self._user = user
        self._pwd = pwd
        self._attr_device_info = device_info

    def _fetch_cmd(self, command: str) -> str | None:
        try:
            response = request("GET", self._ip, self._user, self._pwd, command, timeout=10)
            if response.status_code == 200:
                return response.json().get("data", "")
        except Exception as err:
            _LOGGER.error("Fehler beim Abrufen von %s / Kommando %s: %s", self._ip, command, err)
        return None


class JudoFlowRateSensor(JudoIsoftBaseSensor):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Durchfluss"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_flow_rate"
        self._attr_native_unit_of_measurement = "L/h"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:water-pump"

    def update(self):
        data = self._fetch_cmd("6900")
        if data and len(data) >= 12:
            flow_bytes = bytes.fromhex(data[8:12])
            self._attr_native_value = int.from_bytes(flow_bytes, byteorder="little")


class JudoTotalVolume6900Sensor(JudoIsoftBaseSensor):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Gesamtwasserverbrauch (6900)"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_total_volume_6900"
        self._attr_device_class = SensorDeviceClass.WATER
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS

    def update(self):
        data = self._fetch_cmd("6900")
        if data and len(data) >= 20:
            vol_bytes = bytes.fromhex(data[12:20])
            liters = int.from_bytes(vol_bytes, byteorder="little")
            self._attr_native_value = round(liters / 1000.0, 3)


class JudoWaterTempSensor(JudoIsoftBaseSensor):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Wassertemperatur"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_water_temp"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def update(self):
        data = self._fetch_cmd("6900")
        if data and len(data) >= 22:
            self._attr_native_value = int(data[20:22], 16)


class JudoLeakageReasonSensor(JudoIsoftBaseSensor):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Leckagestatus"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_leakage_reason"
        self._attr_icon = "mdi:alert-circle-outline"

    def update(self):
        data = self._fetch_cmd("6900")
        if data and len(data) >= 8:
            reason_code = int(data[6:8], 16)
            self._attr_native_value = LEAKAGE_REASON_MAPPING.get(reason_code, f"Unbekannt (0x{reason_code:02X})")


class JudoDeviceStatusSensor(JudoIsoftBaseSensor):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Status"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_status"
        self._attr_icon = "mdi:water-softener"

    def update(self):
        data = self._fetch_cmd("02")
        if data:
            status_code = int(data[:2], 16) if len(data) >= 2 else 0
            self._attr_native_value = "Bereit / Normalbetrieb" if status_code == 0 else f"Status-Code 0x{status_code:02X}"


class JudoDeviceTypeSensor(JudoIsoftBaseSensor):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Gerätetyp"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_device_type"
        self._attr_icon = "mdi:chip"

    def update(self):
        data = self._fetch_cmd("01")
        if data and len(data) >= 2:
            self._attr_native_value = f"0x{data[:2]}"


class JudoFirmwareVersionSensor(JudoIsoftBaseSensor):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Firmware Version"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_firmware_version"
        self._attr_icon = "mdi:numeric"

    def update(self):
        data = self._fetch_cmd("01")
        if data and len(data) >= 6:
            self._attr_native_value = f"{data[2:4]}.{data[4:6]}"


class JudoTargetHardnessSensor(JudoIsoftBaseSensor):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Wunschwasserhärte"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_target_hardness"
        self._attr_icon = "mdi:water-percent"

    def update(self):
        data = self._fetch_cmd("20")
        if data and len(data) >= 2:
            self._attr_native_value = int(data[:2], 16)


class JudoHardnessUnitSensor(JudoIsoftBaseSensor):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Härteeinheit"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_hardness_unit"
        self._attr_icon = "mdi:atom"

    def update(self):
        data = self._fetch_cmd("20")
        if data and len(data) >= 4:
            unit_code = int(data[2:4], 16)
            self._attr_native_value = HARDNESS_UNIT_MAPPING.get(unit_code, "Unbekannt")


class JudoMaxEntnahmedauerSensor(JudoIsoftBaseSensor):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Max. Entnahmedauer"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_max_entnahmedauer"
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        self._attr_icon = "mdi:timer-sand"

    def update(self):
        data = self._fetch_cmd("3B")
        if data and len(data) >= 4:
            self._attr_native_value = int.from_bytes(bytes.fromhex(data[:4]), byteorder="little")


class JudoMaxEntnahmemengeSensor(JudoIsoftBaseSensor):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Max. Entnahmemenge"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_max_entnahmemenge"
        self._attr_native_unit_of_measurement = UnitOfVolume.LITERS
        self._attr_icon = "mdi:water-minus"

    def update(self):
        data = self._fetch_cmd("3B")
        if data and len(data) >= 8:
            self._attr_native_value = int.from_bytes(bytes.fromhex(data[4:8]), byteorder="little")


class JudoMaxVolumenstromSensor(JudoIsoftBaseSensor):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Max. Volumenstrom"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_max_volumenstrom"
        self._attr_native_unit_of_measurement = "L/h"
        self._attr_icon = "mdi:speedometer"

    def update(self):
        data = self._fetch_cmd("3B")
        if data and len(data) >= 12:
            self._attr_native_value = int.from_bytes(bytes.fromhex(data[8:12]), byteorder="little")


class JudoSaltWeightSensor(JudoIsoftBaseSensor):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Salzgewicht"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_salt_weight"
        self._attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS
        self._attr_icon = "mdi:salt-shaker"

    def update(self):
        data = self._fetch_cmd("94")
        if data and len(data) >= 4:
            grams = int.from_bytes(bytes.fromhex(data[:4]), byteorder="little")
            self._attr_native_value = round(grams / 1000.0, 1)


class JudoSaltRangeSensor(JudoIsoftBaseSensor):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Salzreichweite"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_salt_range"
        self._attr_native_unit_of_measurement = UnitOfTime.DAYS
        self._attr_icon = "mdi:calendar-clock"

    def update(self):
        data = self._fetch_cmd("94")
        if data and len(data) >= 8:
            self._attr_native_value = int.from_bytes(bytes.fromhex(data[4:8]), byteorder="little")


class JudoSaltWarningThresholdSensor(JudoIsoftBaseSensor):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Salzmangel Warnschwelle"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_salt_warning_threshold"
        self._attr_native_unit_of_measurement = UnitOfTime.DAYS
        self._attr_icon = "mdi:alert-outline"

    def update(self):
        data = self._fetch_cmd("94")
        if data and len(data) >= 12:
            self._attr_native_value = int.from_bytes(bytes.fromhex(data[8:12]), byteorder="little")


class JudoTotalVolumeSensor(JudoIsoftBaseSensor):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Gesamtwassermenge"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_total_water_volume"
        self._attr_device_class = SensorDeviceClass.WATER
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS

    def update(self):
        data = self._fetch_cmd("3F")
        if data and len(data) >= 8:
            liters = int.from_bytes(bytes.fromhex(data[:8]), byteorder="little")
            self._attr_native_value = round(liters / 1000.0, 3)


class JudoSoftWaterVolumeSensor(JudoIsoftBaseSensor):
    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(entry, device_info, ip, user, pwd)
        self._attr_name = "i-soft PRO Weichwassermenge"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_soft_water_volume"
        self._attr_device_class = SensorDeviceClass.WATER
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS

    def update(self) -> None:
        data = self._fetch_cmd("3F")
        if data and len(data) >= 16:
            liters = int.from_bytes(bytes.fromhex(data[8:16]), byteorder="little")
            self._attr_native_value = round(liters / 1000.0, 3)

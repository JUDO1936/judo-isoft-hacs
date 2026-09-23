"""JUDO sensors."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import UnitOfTime, UnitOfVolume
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CMD_6900_READ,
    CMD_COMMISSIONING_DATE,
    CMD_DEVICE_TYPE,
    CMD_HARDNESS,
    CMD_HARDNESS_UNIT_READ,
    CMD_OPERATING_HOURS,
    CMD_SALT,
    CMD_SOFTWARE_VERSION,
    CMD_SOFTENED_WATER,
    CMD_TOTAL_WATER,
    DEVICE_TYPES,
    DOMAIN,
    HARDNESS_UNIT_OPTIONS,
)
from .coordinator import JudoCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: JudoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            JudoConnectionSensor(coordinator),
            JudoWaterSensor(coordinator, "Gesamtwassermenge", CMD_TOTAL_WATER),
            JudoWaterSensor(coordinator, "Weichwassermenge", CMD_SOFTENED_WATER),
            JudoSaltWeightSensor(coordinator),
            JudoSaltRangeSensor(coordinator),
            JudoHardnessSensor(coordinator),
            JudoSoftwareVersionSensor(coordinator),
            JudoDeviceTypeSensor(coordinator),
            JudoOperatingHoursSensor(coordinator),
            JudoCommissioningDateSensor(coordinator),
            Judo6900RawSensor(coordinator),
            Judo6900ByteCountSensor(coordinator),
            Judo6900U16Sensor(coordinator),
            Judo6900U32Sensor(coordinator),
        ]
    )


class JudoEntity(CoordinatorEntity[JudoCoordinator], SensorEntity):
    """Common JUDO sensor entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: JudoCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device_identifier)},
            "name": "JUDO i-soft PRO / PRO L",
            "manufacturer": "JUDO Wasseraufbereitung",
            "model": self._model_name(),
        }

    @property
    def available(self) -> bool:
        return self.coordinator.available and super().available

    def _model_name(self) -> str:
        raw = self.coordinator.value(CMD_DEVICE_TYPE)
        if raw and len(raw) >= 2:
            try:
                return DEVICE_TYPES.get(int(raw[:2], 16), "JUDO i-soft PRO / PRO L")
            except ValueError:
                pass
        return "JUDO i-soft PRO / PRO L"


class JudoConnectionSensor(JudoEntity):
    _attr_name = "Verbindungsstatus"
    _attr_unique_id = f"{DOMAIN}_connection_status"
    _attr_icon = "mdi:lan-connect"

    @property
    def native_value(self) -> str:
        return "Online" if self.coordinator.available else "Offline"

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        return {
            "host": self.coordinator.api.host,
            "port": str(self.coordinator.api.port),
            "letzte_erfolgreiche_abfrage": (
                self.coordinator.last_success.isoformat()
                if self.coordinator.last_success
                else None
            ),
        }


class JudoWaterSensor(JudoEntity):
    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS

    def __init__(self, coordinator: JudoCoordinator, name: str, command: str) -> None:
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{command.lower()}_m3"
        self._attr_icon = "mdi:water"
        self._command = command

    @property
    def native_value(self) -> float | None:
        raw = self.coordinator.value(self._command)
        if not raw or len(raw) < 8:
            return None
        try:
            liters = int.from_bytes(bytes.fromhex(raw[:8]), "little")
        except ValueError:
            return None
        return round(liters / 1000.0, 3)


class JudoSaltWeightSensor(JudoEntity):
    _attr_native_unit_of_measurement = "kg"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:sack"
    _attr_name = "Salzgewicht"
    _attr_unique_id = f"{DOMAIN}_salt_weight"

    @property
    def native_value(self) -> float | None:
        raw = self.coordinator.value(CMD_SALT)
        if not raw or len(raw) < 8:
            return None
        try:
            grams = int.from_bytes(bytes.fromhex(raw[:4]), "little")
        except ValueError:
            return None
        return round(grams / 1000.0, 2)


class JudoSaltRangeSensor(JudoEntity):
    _attr_native_unit_of_measurement = UnitOfTime.DAYS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:calendar-clock"
    _attr_name = "Salzreichweite"
    _attr_unique_id = f"{DOMAIN}_salt_range"

    @property
    def native_value(self) -> int | None:
        raw = self.coordinator.value(CMD_SALT)
        if not raw or len(raw) < 8:
            return None
        try:
            return int.from_bytes(bytes.fromhex(raw[4:8]), "little")
        except ValueError:
            return None


class JudoIntegerSensor(JudoEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: JudoCoordinator, name: str, command: str, unit: str, icon: str) -> None:
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{command.lower()}_sensor"
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._command = command

    @property
    def native_value(self) -> int | None:
        raw = self.coordinator.value(self._command)
        if not raw:
            return None
        try:
            return int.from_bytes(bytes.fromhex(raw), "little")
        except ValueError:
            return None


class JudoHardnessSensor(JudoEntity):
    _attr_icon = "mdi:water-opacity"
    _attr_name = "Wunschwasserhärte"
    _attr_unique_id = f"{DOMAIN}_hardness"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> str | None:
        raw = self.coordinator.value(CMD_HARDNESS_UNIT_READ)
        try:
            code = str(int(raw[:2], 16)) if raw else "0"
            return HARDNESS_UNIT_OPTIONS.get(code, "°dH")
        except ValueError:
            return "°dH"

    @property
    def native_value(self) -> int | None:
        raw = self.coordinator.value(CMD_HARDNESS)
        if not raw or len(raw) < 4:
            return None
        try:
            return int.from_bytes(bytes.fromhex(raw[:4]), "little")
        except ValueError:
            return None


class JudoSoftwareVersionSensor(JudoEntity):
    _attr_name = "Software-Version"
    _attr_unique_id = f"{DOMAIN}_software_version"
    _attr_icon = "mdi:chip"

    @property
    def native_value(self) -> str | None:
        raw = self.coordinator.value(CMD_SOFTWARE_VERSION)
        if not raw or len(raw) < 6:
            return None
        try:
            b = bytes.fromhex(raw[:6])
        except ValueError:
            return None
        # JUDO PRO example: 0C0001 => 1.0.12
        return f"{b[2]}.{b[1]}.{b[0]}"


class JudoDeviceTypeSensor(JudoEntity):
    _attr_name = "Gerätetyp"
    _attr_unique_id = f"{DOMAIN}_device_type"
    _attr_icon = "mdi:water-softener"

    @property
    def native_value(self) -> str | None:
        raw = self.coordinator.value(CMD_DEVICE_TYPE)
        if not raw:
            return None
        try:
            code = int(raw[:2], 16)
        except ValueError:
            return None
        return DEVICE_TYPES.get(code, f"0x{code:02X}")

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        raw = self.coordinator.value(CMD_DEVICE_TYPE)
        return {"hex": raw, "device_number": self.coordinator.value(CMD_DEVICE_NUMBER)}


class JudoOperatingHoursSensor(JudoEntity):
    _attr_native_unit_of_measurement = "h"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_name = "Betriebsstunden"
    _attr_unique_id = f"{DOMAIN}_operating_hours"
    _attr_icon = "mdi:clock-outline"

    @property
    def native_value(self) -> float | None:
        raw = self.coordinator.value(CMD_OPERATING_HOURS)
        if not raw or len(raw) < 8:
            return None
        try:
            b = bytes.fromhex(raw[:8])
            minutes = b[0]
            hours = b[1]
            days = int.from_bytes(b[2:4], "little")
        except (ValueError, IndexError):
            return None
        return round(days * 24 + hours + minutes / 60.0, 2)


class JudoCommissioningDateSensor(JudoEntity):
    _attr_name = "Inbetriebnahmedatum"
    _attr_unique_id = f"{DOMAIN}_commissioning_date"
    _attr_icon = "mdi:calendar-check"

    @property
    def native_value(self) -> str | None:
        raw = self.coordinator.value(CMD_COMMISSIONING_DATE)
        if not raw or len(raw) < 8:
            return None
        try:
            b = bytes.fromhex(raw[:8])
            day = b[0]
            month = b[1]
            year = int.from_bytes(b[2:4], "little")
        except (ValueError, IndexError):
            return None
        if not (1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2200):
            return None
        return f"{year:04d}-{month:02d}-{day:02d}"


class Judo6900Base(JudoEntity):
    """Base for the future 6900 group command."""

    _attr_icon = "mdi:database-search"

    def _raw(self) -> bytes | None:
        raw = self.coordinator.value(CMD_6900_READ)
        if not raw or len(raw) % 2:
            return None
        try:
            return bytes.fromhex(raw)
        except ValueError:
            return None


class Judo6900RawSensor(Judo6900Base):
    _attr_name = "6900 Rohdaten"
    _attr_unique_id = f"{DOMAIN}_6900_raw"
    _attr_icon = "mdi:hexadecimal"

    @property
    def native_value(self) -> str | None:
        raw = self.coordinator.value(CMD_6900_READ)
        return raw or None


class Judo6900ByteCountSensor(Judo6900Base):
    _attr_name = "6900 Byte-Anzahl"
    _attr_unique_id = f"{DOMAIN}_6900_byte_count"
    _attr_native_unit_of_measurement = "B"

    @property
    def native_value(self) -> int | None:
        raw = self._raw()
        return len(raw) if raw is not None else None


class Judo6900U16Sensor(Judo6900Base):
    _attr_name = "6900 16-bit Werte"
    _attr_unique_id = f"{DOMAIN}_6900_u16"

    @property
    def native_value(self) -> str | None:
        raw = self._raw()
        if not raw:
            return None
        values = [str(int.from_bytes(raw[i:i + 2], "little")) for i in range(0, len(raw) - 1, 2)]
        return ", ".join(values) if values else None


class Judo6900U32Sensor(Judo6900Base):
    _attr_name = "6900 32-bit Werte"
    _attr_unique_id = f"{DOMAIN}_6900_u32"

    @property
    def native_value(self) -> str | None:
        raw = self._raw()
        if not raw or len(raw) < 4:
            return None
        values = [
            str(int.from_bytes(raw[i:i + 4], "little"))
            for i in range(0, len(raw) - 3, 4)
        ]
        return ", ".join(values) if values else None

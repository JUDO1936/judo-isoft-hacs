"""JUDO i-soft PRO / PRO L sensors."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTime, UnitOfTemperature, UnitOfVolume
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CMD_6900_READ,
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
    entity_prefix,
)
from .coordinator import JudoCoordinator
from .protocol import (
    Judo6900Status,
    leakage_reason_label,
    leakage_status_details,
    leakage_status_label,
    scene_label,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: JudoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            JudoWaterSensor(coordinator, entry, "Gesamtwassermenge", CMD_TOTAL_WATER, "28_m3", "gesamtwassermenge"),
            JudoWaterSensor(coordinator, entry, "Weichwassermenge", CMD_SOFTENED_WATER, "29_m3", "weichwassermenge"),
            JudoSaltWeightSensor(coordinator, entry),
            JudoSaltRangeSensor(coordinator, entry),
            JudoHardnessSensor(coordinator, entry),
            JudoSoftwareVersionSensor(coordinator, entry),
            JudoDeviceTypeSensor(coordinator, entry),
            JudoOperatingHoursSensor(coordinator, entry),
            JudoActiveSceneSensor(coordinator, entry),
            JudoLeakageStatusSensor(coordinator, entry),
            JudoLeakageReasonSensor(coordinator, entry),
            JudoCurrentWaterFlowSensor(coordinator, entry),
            JudoWaterTemperatureSensor(coordinator, entry),
        ]
    )


class JudoEntity(CoordinatorEntity[JudoCoordinator], SensorEntity):
    """Common JUDO sensor entity with per-endpoint default entity IDs."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: JudoCoordinator,
        entry: ConfigEntry,
        *,
        unique_suffix: str,
        entity_key: str,
        name: str,
    ) -> None:
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{unique_suffix}_{entry.entry_id}"
        self._attr_default_entity_id = (
            f"sensor.{entity_prefix(coordinator.api.host, coordinator.api.port)}_{entity_key}"
        )
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": coordinator.device_name,
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


class JudoWaterSensor(JudoEntity):
    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
    _attr_suggested_display_precision = 3
    _attr_icon = "mdi:water"

    def __init__(self, coordinator, entry, name, command, unique_suffix, entity_key) -> None:
        super().__init__(
            coordinator,
            entry,
            unique_suffix=unique_suffix,
            entity_key=entity_key,
            name=name,
        )
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
    _attr_suggested_display_precision = 2
    _attr_icon = "mdi:sack"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator,
            entry,
            unique_suffix="salt_weight",
            entity_key="salzgewicht",
            name="Salzgewicht",
        )

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

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator,
            entry,
            unique_suffix="salt_range",
            entity_key="salzreichweite",
            name="Salzreichweite",
        )

    @property
    def native_value(self) -> int | None:
        raw = self.coordinator.value(CMD_SALT)
        if not raw or len(raw) < 8:
            return None
        try:
            return int.from_bytes(bytes.fromhex(raw[4:8]), "little")
        except ValueError:
            return None


class JudoHardnessSensor(JudoEntity):
    _attr_icon = "mdi:water-opacity"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator,
            entry,
            unique_suffix="hardness",
            entity_key="wunschwasserharte",
            name="Wunschwasserhärte",
        )

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
    _attr_icon = "mdi:chip"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator,
            entry,
            unique_suffix="software_version",
            entity_key="software_version",
            name="Software-Version",
        )

    @property
    def native_value(self) -> str | None:
        raw = self.coordinator.value(CMD_SOFTWARE_VERSION)
        if not raw or len(raw) < 6:
            return None
        try:
            b = bytes.fromhex(raw[:6])
        except ValueError:
            return None
        return f"{b[2]}.{b[1]}.{b[0]}"


class JudoDeviceTypeSensor(JudoEntity):
    _attr_icon = "mdi:water-softener"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator,
            entry,
            unique_suffix="device_type",
            entity_key="geraetetyp",
            name="Gerätetyp",
        )

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
        return {"hex": raw}


class JudoOperatingHoursSensor(JudoEntity):
    _attr_native_unit_of_measurement = "h"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:clock-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator,
            entry,
            unique_suffix="operating_hours",
            entity_key="betriebsstunden",
            name="Betriebsstunden",
        )

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


class Judo6900Entity(JudoEntity):
    """Common base for the user-requested values from the single 6900 read."""

    def _status(self) -> Judo6900Status | None:
        return self.coordinator.status_6900

    @property
    def available(self) -> bool:
        return super().available and self._status() is not None


class JudoActiveSceneSensor(Judo6900Entity):
    _attr_icon = "mdi:play-circle-outline"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator,
            entry,
            unique_suffix="active_scene",
            entity_key="aktive_szene",
            name="Aktive Szene",
        )

    @property
    def native_value(self) -> str | None:
        status = self._status()
        return scene_label(status.active_scene) if status else None

    @property
    def extra_state_attributes(self) -> dict[str, str | int | None]:
        status = self._status()
        if not status:
            return {}
        return {
            "szenencode": f"{status.active_scene:X}",
            "szenenoptionen": f"0x{status.active_scene_options:02X}",
        }


class JudoLeakageStatusSensor(Judo6900Entity):
    _attr_icon = "mdi:shield-water"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator,
            entry,
            unique_suffix="leakage_status",
            entity_key="leckageschutz_status",
            name="Globaler Leckageschutz",
        )

    @property
    def native_value(self) -> str | None:
        status = self._status()
        return leakage_status_label(status.leakage_status) if status else None

    @property
    def extra_state_attributes(self) -> dict[str, str | int | list[str]]:
        status = self._status()
        if not status:
            return {}
        return {
            "status_hex": f"0x{status.leakage_status:02X}",
            "aktive_funktionen": leakage_status_details(status.leakage_status),
        }


class JudoLeakageReasonSensor(Judo6900Entity):
    _attr_icon = "mdi:alert-decagram-outline"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator,
            entry,
            unique_suffix="leakage_reason",
            entity_key="leckagegrund",
            name="Leckagegrund",
        )

    @property
    def native_value(self) -> str | None:
        status = self._status()
        return leakage_reason_label(status.leakage_reason) if status else None

    @property
    def extra_state_attributes(self) -> dict[str, str | int]:
        status = self._status()
        if not status:
            return {}
        return {"grund_hex": f"0x{status.leakage_reason:02X}"}


class JudoCurrentWaterFlowSensor(Judo6900Entity):
    _attr_native_unit_of_measurement = "L/h"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 0
    _attr_icon = "mdi:water-pump"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator,
            entry,
            unique_suffix="current_water_flow",
            entity_key="aktueller_wasserdurchfluss",
            name="Aktueller Wasserdurchfluss",
        )

    @property
    def native_value(self) -> int | None:
        status = self._status()
        return status.current_water_flow_l_h if status else None


class JudoWaterTemperatureSensor(Judo6900Entity):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1
    _attr_icon = "mdi:thermometer-water"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator,
            entry,
            unique_suffix="water_temperature",
            entity_key="wassertemperatur",
            name="Wassertemperatur",
        )

    @property
    def native_value(self) -> int | None:
        status = self._status()
        return status.current_water_temperature_c if status else None

"""Writable JUDO settings exposed as Home Assistant number entities."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CMD_HARDNESS,
    CMD_HARDNESS_WRITE,
    CMD_MAX_DRAW_AMOUNT,
    CMD_MAX_DRAW_TIME,
    CMD_MAX_FLOW,
    CMD_SALT_WARNING,
    DOMAIN,
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
            JudoWritableNumber(
                coordinator,
                "Salzmangel-Warnschwelle",
                CMD_SALT_WARNING,
                0,
                255,
                1,
                "d",
                "mdi:alert-circle-outline",
                1,
            ),
            JudoWritableNumber(
                coordinator,
                "Wunschwasserhärte",
                CMD_HARDNESS,
                0,
                255,
                1,
                None,
                "mdi:water-opacity",
                2,
                write_command=CMD_HARDNESS_WRITE,
            ),
            JudoWritableNumber(
                coordinator,
                "Max. Entnahmedauer",
                CMD_MAX_DRAW_TIME,
                0,
                255,
                1,
                "min",
                "mdi:timer-outline",
                1,
            ),
            JudoWritableNumber(
                coordinator,
                "Max. Entnahmemenge",
                CMD_MAX_DRAW_AMOUNT,
                0,
                3000,
                1,
                "L",
                "mdi:cup-water",
                2,
            ),
            JudoWritableNumber(
                coordinator,
                "Max. Volumenstrom",
                CMD_MAX_FLOW,
                0,
                5000,
                1,
                "L/h",
                "mdi:water-pump",
                2,
            ),
        ]
    )


class JudoWritableNumber(CoordinatorEntity[JudoCoordinator], NumberEntity):
    _attr_has_entity_name = True
    _attr_mode = NumberMode.BOX
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: JudoCoordinator,
        name: str,
        read_command: str,
        minimum: float,
        maximum: float,
        step: float,
        unit: str | None,
        icon: str,
        data_bytes: int,
        write_command: str | None = None,
    ) -> None:
        super().__init__(coordinator)
        self._read_command = read_command
        self._write_command = write_command or read_command
        self._data_bytes = data_bytes
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{read_command.lower()}_number"
        self._attr_native_min_value = minimum
        self._attr_native_max_value = maximum
        self._attr_native_step = step
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device_identifier)},
            "name": "JUDO i-soft PRO / PRO L",
            "manufacturer": "JUDO Wasseraufbereitung",
        }

    @property
    def available(self) -> bool:
        return self.coordinator.available

    @property
    def native_value(self) -> float | None:
        raw = self.coordinator.value(self._read_command)
        if not raw:
            return None
        try:
            return float(int.from_bytes(bytes.fromhex(raw), "little"))
        except ValueError:
            return None

    async def async_set_native_value(self, value: float) -> None:
        integer_value = int(round(value))
        data = integer_value.to_bytes(self._data_bytes, "little", signed=False).hex().upper()
        recheck = self._read_command
        await self.coordinator.async_write_command(
            self._write_command, data, recheck_command=recheck
        )
        self.async_write_ha_state()

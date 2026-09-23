"""JUDO leak protection switch."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CMD_LEAK_CLOSE, CMD_LEAK_OPEN, DOMAIN
from .coordinator import JudoCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: JudoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([JudoLeakProtectionSwitch(coordinator)])


class JudoLeakProtectionSwitch(CoordinatorEntity[JudoCoordinator], SwitchEntity):
    """Optimistic switch because the documented PRO read table has no direct status command."""

    _attr_has_entity_name = True
    _attr_name = "Leckageschutz"
    _attr_unique_id = f"{DOMAIN}_leak_protection"
    _attr_icon = "mdi:shield-water"
    _attr_assumed_state = True

    def __init__(self, coordinator: JudoCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device_identifier)},
            "name": "JUDO i-soft PRO / PRO L",
            "manufacturer": "JUDO Wasseraufbereitung",
        }

    @property
    def available(self) -> bool:
        return self.coordinator.available

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.leak_protection_state)

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_write_command(CMD_LEAK_OPEN)
        self.coordinator.set_leak_protection_state(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_write_command(CMD_LEAK_CLOSE)
        self.coordinator.set_leak_protection_state(False)

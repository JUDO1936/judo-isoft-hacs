"""JUDO action buttons."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CMD_LEAK_CLOSE, CMD_LEAK_OPEN, CMD_REGENERATION, CMD_SCENE, DOMAIN
from .coordinator import JudoCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: JudoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            JudoSceneActivateButton(coordinator),
            JudoRegenerationButton(coordinator),
            JudoLeakOpenButton(coordinator),
            JudoLeakCloseButton(coordinator),
        ]
    )


class JudoButtonBase(CoordinatorEntity[JudoCoordinator], ButtonEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: JudoCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device_identifier)},
            "name": "JUDO i-soft PRO / PRO L",
            "manufacturer": "JUDO Wasseraufbereitung",
        }


class JudoSceneActivateButton(JudoButtonBase):
    _attr_name = "Szene aktivieren"
    _attr_unique_id = f"{DOMAIN}_scene_activate"
    _attr_icon = "mdi:play-circle"

    async def async_press(self) -> None:
        scene = self.coordinator.selected_scene
        duration = self.coordinator.selected_scene_duration
        if scene == "0":
            raise HomeAssistantError(
                "Szene 0 ist die Grundszene und muss nicht per Sofortaktivierung gesetzt werden."
            )
        await self.coordinator.async_write_command(
            CMD_SCENE,
            f"{int(scene, 16):02X}{duration}",
        )


class JudoRegenerationButton(JudoButtonBase):
    _attr_name = "Regeneration starten"
    _attr_unique_id = f"{DOMAIN}_regeneration_start"
    _attr_icon = "mdi:refresh"

    async def async_press(self) -> None:
        await self.coordinator.async_write_command(CMD_REGENERATION, "00")


class JudoLeakOpenButton(JudoButtonBase):
    _attr_name = "Leckageschutz öffnen"
    _attr_unique_id = f"{DOMAIN}_leak_open_button"
    _attr_icon = "mdi:valve-open"

    async def async_press(self) -> None:
        await self.coordinator.async_write_command(CMD_LEAK_OPEN)
        self.coordinator.set_leak_protection_state(True)


class JudoLeakCloseButton(JudoButtonBase):
    _attr_name = "Leckageschutz schließen"
    _attr_unique_id = f"{DOMAIN}_leak_close_button"
    _attr_icon = "mdi:valve-closed"

    async def async_press(self) -> None:
        await self.coordinator.async_write_command(CMD_LEAK_CLOSE)
        self.coordinator.set_leak_protection_state(False)

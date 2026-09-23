"""JUDO action buttons."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CMD_6900_READ, CMD_LEAK_CLOSE, CMD_LEAK_OPEN, CMD_REGENERATION, CMD_SCENE, DOMAIN, entity_prefix
from .coordinator import JudoCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: JudoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            JudoSceneActivateButton(coordinator, entry),
            JudoRegenerationButton(coordinator, entry),
            JudoLeakOpenButton(coordinator, entry),
            JudoLeakCloseButton(coordinator, entry),
        ]
    )


class JudoButtonBase(CoordinatorEntity[JudoCoordinator], ButtonEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: JudoCoordinator, entry: ConfigEntry, *, unique_suffix: str, entity_key: str, name: str) -> None:
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{unique_suffix}_{entry.entry_id}"
        self._attr_default_entity_id = (
            f"button.{entity_prefix(coordinator.api.host, coordinator.api.port)}_{entity_key}"
        )
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": coordinator.device_name,
            "manufacturer": "JUDO Wasseraufbereitung",
        }

    @property
    def available(self) -> bool:
        return self.coordinator.available


class JudoSceneActivateButton(JudoButtonBase):
    _attr_icon = "mdi:play-circle"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator, entry,
            unique_suffix="scene_activate",
            entity_key="szene_aktivieren",
            name="Szene aktivieren",
        )

    async def async_press(self) -> None:
        scene = self.coordinator.selected_scene
        duration = self.coordinator.selected_scene_duration
        if scene == "0":
            raise HomeAssistantError(
                "Szene 0 ist die Grundszene und kann nicht per Sofortaktivierung gestartet werden."
            )
        await self.coordinator.async_write_command(
            CMD_SCENE,
            f"{int(scene, 16):02X}{duration}",
            recheck_command=CMD_6900_READ,
        )


class JudoRegenerationButton(JudoButtonBase):
    _attr_icon = "mdi:refresh"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator, entry,
            unique_suffix="regeneration_start",
            entity_key="regeneration_starten",
            name="Regeneration starten",
        )

    async def async_press(self) -> None:
        await self.coordinator.async_write_command(CMD_REGENERATION, "00")


class JudoLeakOpenButton(JudoButtonBase):
    _attr_icon = "mdi:valve-open"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator, entry,
            unique_suffix="leak_open_button",
            entity_key="leckageschutz_offnen",
            name="Leckageschutz öffnen",
        )

    async def async_press(self) -> None:
        await self.coordinator.async_write_command(
            CMD_LEAK_OPEN, recheck_command=CMD_6900_READ
        )


class JudoLeakCloseButton(JudoButtonBase):
    _attr_icon = "mdi:valve-closed"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator, entry,
            unique_suffix="leak_close_button",
            entity_key="leckageschutz_schliessen",
            name="Leckageschutz schließen",
        )

    async def async_press(self) -> None:
        await self.coordinator.async_write_command(
            CMD_LEAK_CLOSE, recheck_command=CMD_6900_READ
        )

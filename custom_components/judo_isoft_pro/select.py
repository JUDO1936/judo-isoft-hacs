"""JUDO select entities for scene, scene duration and hardness unit."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CMD_HARDNESS_UNIT_READ,
    CMD_HARDNESS_UNIT_WRITE,
    DOMAIN,
    HARDNESS_UNIT_NAME_TO_CODE,
    HARDNESS_UNIT_OPTIONS,
    SCENE_DURATION_NAME_TO_CODE,
    SCENE_DURATION_OPTIONS,
    SCENE_NAME_TO_CODE,
    SCENE_OPTIONS,
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
            JudoSceneSelect(coordinator),
            JudoSceneDurationSelect(coordinator),
            JudoHardnessUnitSelect(coordinator),
        ]
    )


class JudoSelectBase(CoordinatorEntity[JudoCoordinator], SelectEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: JudoCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device_identifier)},
            "name": "JUDO i-soft PRO / PRO L",
            "manufacturer": "JUDO Wasseraufbereitung",
        }


class JudoSceneSelect(JudoSelectBase):
    _attr_name = "Szenenauswahl"
    _attr_unique_id = f"{DOMAIN}_scene_select"
    _attr_icon = "mdi:water-sync"
    _attr_options = list(SCENE_OPTIONS.values())

    @property
    def current_option(self) -> str:
        return SCENE_OPTIONS.get(self.coordinator.selected_scene, SCENE_OPTIONS["0"])

    async def async_select_option(self, option: str) -> None:
        code = SCENE_NAME_TO_CODE[option]
        self.coordinator.set_scene_selection(
            code, self.coordinator.selected_scene_duration
        )
        self.async_write_ha_state()


class JudoSceneDurationSelect(JudoSelectBase):
    _attr_name = "Szenendauer"
    _attr_unique_id = f"{DOMAIN}_scene_duration"
    _attr_icon = "mdi:timer-outline"
    _attr_options = list(SCENE_DURATION_OPTIONS.values())

    @property
    def current_option(self) -> str:
        return SCENE_DURATION_OPTIONS.get(
            self.coordinator.selected_scene_duration,
            SCENE_DURATION_OPTIONS["0100"],
        )

    async def async_select_option(self, option: str) -> None:
        code = SCENE_DURATION_NAME_TO_CODE[option]
        self.coordinator.set_scene_selection(
            self.coordinator.selected_scene, code
        )
        self.async_write_ha_state()


class JudoHardnessUnitSelect(JudoSelectBase):
    _attr_name = "Härteeinheit"
    _attr_unique_id = f"{DOMAIN}_hardness_unit"
    _attr_icon = "mdi:format-letter-case"
    _attr_options = list(HARDNESS_UNIT_OPTIONS.values())

    @property
    def current_option(self) -> str:
        raw = self.coordinator.value(CMD_HARDNESS_UNIT_READ)
        if raw:
            try:
                return HARDNESS_UNIT_OPTIONS.get(str(int(raw[:2], 16)), "°dH")
            except ValueError:
                pass
        return "°dH"

    async def async_select_option(self, option: str) -> None:
        code = HARDNESS_UNIT_NAME_TO_CODE[option]
        await self.coordinator.async_write_command(
            CMD_HARDNESS_UNIT_WRITE,
            f"{int(code):02X}",
            recheck_command=CMD_HARDNESS_UNIT_READ,
        )
        self.async_write_ha_state()

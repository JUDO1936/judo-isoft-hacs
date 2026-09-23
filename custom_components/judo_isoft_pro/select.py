"""JUDO select entities for scenes and hardness units."""

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
    entity_prefix,
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
            JudoSceneSelect(coordinator, entry),
            JudoSceneDurationSelect(coordinator, entry),
            JudoHardnessUnitSelect(coordinator, entry),
        ]
    )


class JudoSelectBase(CoordinatorEntity[JudoCoordinator], SelectEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: JudoCoordinator, entry: ConfigEntry, *, unique_suffix: str, entity_key: str, name: str) -> None:
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{unique_suffix}_{entry.entry_id}"
        self._attr_default_entity_id = (
            f"select.{entity_prefix(coordinator.api.host, coordinator.api.port)}_{entity_key}"
        )
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": coordinator.device_name,
            "manufacturer": "JUDO Wasseraufbereitung",
        }

    @property
    def available(self) -> bool:
        return self.coordinator.available


class JudoSceneSelect(JudoSelectBase):
    _attr_icon = "mdi:water-sync"
    _attr_options = list(SCENE_OPTIONS.values())

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator, entry,
            unique_suffix="scene_select",
            entity_key="szenenauswahl",
            name="Szenenauswahl",
        )

    @property
    def current_option(self) -> str:
        return SCENE_OPTIONS.get(self.coordinator.selected_scene, SCENE_OPTIONS["0"])

    async def async_select_option(self, option: str) -> None:
        self.coordinator.set_scene_selection(
            SCENE_NAME_TO_CODE[option], self.coordinator.selected_scene_duration
        )
        self.async_write_ha_state()


class JudoSceneDurationSelect(JudoSelectBase):
    _attr_icon = "mdi:timer-outline"
    _attr_options = list(SCENE_DURATION_OPTIONS.values())

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator, entry,
            unique_suffix="scene_duration",
            entity_key="szenendauer",
            name="Szenendauer",
        )

    @property
    def current_option(self) -> str:
        return SCENE_DURATION_OPTIONS.get(
            self.coordinator.selected_scene_duration,
            SCENE_DURATION_OPTIONS["0100"],
        )

    async def async_select_option(self, option: str) -> None:
        self.coordinator.set_scene_selection(
            self.coordinator.selected_scene, SCENE_DURATION_NAME_TO_CODE[option]
        )
        self.async_write_ha_state()


class JudoHardnessUnitSelect(JudoSelectBase):
    _attr_icon = "mdi:format-letter-case"
    _attr_options = list(HARDNESS_UNIT_OPTIONS.values())

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator, entry,
            unique_suffix="hardness_unit",
            entity_key="harteeinheit",
            name="Härteeinheit",
        )

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

"""JUDO i-soft PRO / PRO L Home Assistant integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import JudoApi
from .const import (
    CONF_NAME,
    DEFAULT_PASSWORD,
    DEFAULT_PORT,
    DEFAULT_USERNAME,
    DOMAIN,
)
from .coordinator import JudoCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.SELECT,
    Platform.NUMBER,
    Platform.BUTTON,
]

_OBSOLETE_UNIQUE_SUFFIXES = (
    "connection_status",
    "commissioning_date",
    "6900_raw",
    "6900_byte_count",
    "6900_u16",
    "6900_u32",
    "leak_protection",
)


async def _async_remove_obsolete_entities(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    """Remove entities deliberately dropped from the public integration."""
    registry = er.async_get(hass)
    obsolete = {
        f"{DOMAIN}_{suffix}_{entry.entry_id}"
        for suffix in _OBSOLETE_UNIQUE_SUFFIXES
    }
    for entity in er.async_entries_for_config_entry(registry, entry.entry_id):
        if entity.unique_id in obsolete:
            registry.async_remove(entity.entity_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up one JUDO device from a config entry."""
    api = JudoApi(
        async_get_clientsession(hass),
        host=entry.data["host"],
        port=entry.data.get("port", DEFAULT_PORT),
        username=entry.data.get("username", DEFAULT_USERNAME),
        password=entry.data.get("password", DEFAULT_PASSWORD),
    )
    coordinator = JudoCoordinator(
        hass, api, device_name=entry.data.get(CONF_NAME, entry.title)
    )
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await coordinator.async_config_entry_first_refresh()
    await _async_remove_obsolete_entities(hass, entry)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload one JUDO config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: JudoCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        for task in coordinator._recheck_tasks.values():
            task.cancel()
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    return unload_ok

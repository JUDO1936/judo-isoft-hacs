"""JUDO i-soft PRO / PRO L Home Assistant integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import JudoApi
from .const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
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
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up one JUDO device from a config entry."""
    api = JudoApi(
        async_get_clientsession(hass),
        host=entry.data[CONF_HOST],
        port=entry.data.get(CONF_PORT, DEFAULT_PORT),
        username=entry.data.get(CONF_USERNAME, DEFAULT_USERNAME),
        password=entry.data.get(CONF_PASSWORD, DEFAULT_PASSWORD),
    )
    coordinator = JudoCoordinator(hass, api)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await coordinator.async_config_entry_first_refresh()
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

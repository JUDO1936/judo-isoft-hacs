"""Central serialized coordinator for all JUDO reads and writes."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import JudoApi, JudoApiError
from .const import (
    CMD_6900_READ,
    POLL_COMMANDS,
    POLL_INTERVAL,
    RECHECK_DELAY,
    RECHECKABLE_COMMANDS,
)


class JudoCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll all commands sequentially and preserve last known good values."""

    def __init__(self, hass: HomeAssistant, api: JudoApi) -> None:
        self.api = api
        self._cache: dict[str, str] = {}
        self._errors: dict[str, str] = {}
        self._last_success: dict[str, datetime] = {}
        self._selected_scene = "0"
        self._selected_scene_duration = "0100"
        self._leak_protection_state: bool | None = None
        self._recheck_tasks: dict[str, asyncio.Task[None]] = {}
        self._device_seen = False

        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name="JUDO i-soft PRO REST",
            update_method=self._async_update_data,
            update_interval=POLL_INTERVAL,
        )

    @property
    def available(self) -> bool:
        return self._device_seen

    @property
    def device_identifier(self) -> str:
        return f"{self.api.host}:{self.api.port}"

    @property
    def last_success(self) -> datetime | None:
        """Timestamp of the most recent successful REST response."""
        return max(self._last_success.values()) if self._last_success else None

    @property
    def selected_scene(self) -> str:
        return self._selected_scene

    @property
    def selected_scene_duration(self) -> str:
        return self._selected_scene_duration

    @property
    def leak_protection_state(self) -> bool | None:
        return self._leak_protection_state

    def set_scene_selection(self, scene_code: str, duration_code: str) -> None:
        self._selected_scene = scene_code
        self._selected_scene_duration = duration_code

    def value(self, command: str) -> str | None:
        return self._cache.get(command)

    def error(self, command: str) -> str | None:
        return self._errors.get(command)

    def all_data(self) -> dict[str, str]:
        return dict(self._cache)

    async def _async_update_data(self) -> dict[str, Any]:
        changed: list[str] = []
        for command in POLL_COMMANDS:
            old = self._cache.get(command)
            try:
                if command == CMD_6900_READ:
                    raw = await self.api.read("6900")
                else:
                    raw = await self.api.read(command)
            except JudoApiError as err:
                self._errors[command] = str(err)
                continue

            self._cache[command] = raw
            self._errors.pop(command, None)
            self._last_success[command] = datetime.now(timezone.utc)
            self._device_seen = True

            if old is not None and old != raw and command in RECHECKABLE_COMMANDS:
                changed.append(command)

        for command in changed:
            self.schedule_recheck(command)

        return self._build_data()

    async def async_write_command(
        self,
        command: str,
        data_hex: str = "",
        recheck_command: str | None = None,
    ) -> None:
        """Write a command through the same one-per-second queue."""
        try:
            await self.api.write(command, data_hex)
            self._device_seen = True
        except JudoApiError as err:
            self._errors[command] = str(err)
            raise
        self.schedule_recheck(recheck_command or (command if command in RECHECKABLE_COMMANDS else None))

    def schedule_recheck(self, command: str | None) -> None:
        if not command:
            return
        existing = self._recheck_tasks.get(command)
        if existing and not existing.done():
            return
        self._recheck_tasks[command] = self.hass.async_create_task(
            self._delayed_recheck(command)
        )

    async def _delayed_recheck(self, command: str) -> None:
        try:
            await asyncio.sleep(RECHECK_DELAY)
            try:
                raw = await self.api.read(command)
            except JudoApiError as err:
                self._errors[command] = str(err)
                return
            self._cache[command] = raw
            self._errors.pop(command, None)
            self._last_success[command] = datetime.now(timezone.utc)
            self._device_seen = True
            self.async_set_updated_data(self._build_data())
        finally:
            self._recheck_tasks.pop(command, None)

    def set_leak_protection_state(self, enabled: bool) -> None:
        self._leak_protection_state = enabled
        self.async_set_updated_data(self._build_data())

    def _build_data(self) -> dict[str, Any]:
        return {
            "raw": dict(self._cache),
            "errors": dict(self._errors),
            "last_success": dict(self._last_success),
            "available": self._device_seen,
        }

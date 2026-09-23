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
    MIN_COMMAND_INTERVAL,
    POLL_COMMANDS,
    POLL_INTERVAL,
    RECHECK_DELAY,
    RECHECKABLE_COMMANDS,
)
from .protocol import Judo6900Status, decode_6900


class JudoCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll documented commands sequentially and keep last valid values."""

    def __init__(self, hass: HomeAssistant, api: JudoApi, device_name: str) -> None:
        self.api = api
        self.device_name = device_name.strip() or "JUDO i-soft PRO / PRO L"
        self._cache: dict[str, str] = {}
        self._errors: dict[str, str] = {}
        self._last_success: dict[str, datetime] = {}
        self._selected_scene = "0"
        self._selected_scene_duration = "0100"
        self._recheck_tasks: dict[str, asyncio.Task[None]] = {}
        self._device_seen = False

        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name=f"JUDO i-soft PRO REST {api.host}:{api.port}",
            update_method=self._async_update_data,
            update_interval=POLL_INTERVAL,
            always_update=True,
        )

    @property
    def available(self) -> bool:
        return self._device_seen

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
    def status_6900(self) -> Judo6900Status | None:
        """Return the currently cached and decoded 6900 status."""
        return decode_6900(self._cache.get(CMD_6900_READ))

    def set_scene_selection(self, scene_code: str, duration_code: str) -> None:
        self._selected_scene = scene_code
        self._selected_scene_duration = duration_code

    def value(self, command: str) -> str | None:
        return self._cache.get(command)

    def error(self, command: str) -> str | None:
        return self._errors.get(command)

    async def _read_command(self, command: str) -> str:
        if command == CMD_6900_READ:
            return await self.api.read(CMD_6900_READ)
        return await self.api.read(command)

    async def _async_update_data(self) -> dict[str, Any]:
        changed: list[str] = []

        for command in POLL_COMMANDS:
            old = self._cache.get(command)
            try:
                raw = await self._read_command(command)
            except JudoApiError as err:
                # Keep the last good value. A temporary empty response must
                # never turn an existing sensor value into unavailable.
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
        """Send a write through the same serialized command queue."""
        try:
            await self.api.write(command, data_hex)
            self._device_seen = True
            self._errors.pop(command, None)
        except JudoApiError as err:
            self._errors[command] = str(err)
            raise

        self.schedule_recheck(recheck_command or (
            command if command in RECHECKABLE_COMMANDS else None
        ))

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
                raw = await self._read_command(command)
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

    def _build_data(self) -> dict[str, Any]:
        return {
            "raw": dict(self._cache),
            "errors": dict(self._errors),
            "last_success": dict(self._last_success),
            "available": self._device_seen,
            "min_command_interval": MIN_COMMAND_INTERVAL,
        }

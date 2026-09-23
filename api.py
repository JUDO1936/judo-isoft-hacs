"""Async JUDO local REST API client with strict request serialization."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Iterable
from typing import Any

from aiohttp import BasicAuth, ClientError, ClientSession

from .const import DEFAULT_TIMEOUT, MIN_COMMAND_INTERVAL


class JudoApiError(Exception):
    """Raised when a JUDO REST request fails."""


class JudoApi:
    """JUDO REST client.

    All commands are serialized and separated by at least one second. This
    protects devices where too many simultaneous LAN requests cause missing
    responses.
    """

    def __init__(
        self,
        session: ClientSession,
        host: str,
        port: int,
        username: str,
        password: str,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._session = session
        self.host = host.strip()
        self.port = port
        self._auth = BasicAuth(username, password)
        self._timeout = timeout
        self._lock = asyncio.Lock()
        self._last_request_start = 0.0

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}/api/rest"

    async def _wait_for_request_slot(self) -> None:
        now = time.monotonic()
        wait_time = self._last_request_start + MIN_COMMAND_INTERVAL - now
        if wait_time > 0:
            await asyncio.sleep(wait_time)
        self._last_request_start = time.monotonic()

    async def request(self, path_hex: str) -> str:
        """Perform one REST GET using an already-built hex path."""
        path_hex = path_hex.replace(" ", "").strip().upper()
        if len(path_hex) < 4 or len(path_hex) % 2:
            raise JudoApiError(f"Ungültiger REST-Pfad: {path_hex}")

        url = f"{self.base_url}/{path_hex}"
        async with self._lock:
            await self._wait_for_request_slot()
            try:
                async with self._session.get(
                    url,
                    auth=self._auth,
                    timeout=self._timeout,
                    headers={"Accept": "application/json"},
                ) as response:
                    body = await response.text()
                    if response.status != 200:
                        raise JudoApiError(
                            f"HTTP {response.status} für /api/rest/{path_hex}: {body[:200]}"
                        )
                    try:
                        payload = await response.json(content_type=None)
                    except ValueError as err:
                        raise JudoApiError(
                            f"Ungültige JSON-Antwort für /api/rest/{path_hex}"
                        ) from err
            except asyncio.TimeoutError as err:
                raise JudoApiError(
                    f"Timeout für /api/rest/{path_hex}"
                ) from err
            except ClientError as err:
                raise JudoApiError(
                    f"REST-Abfrage /api/rest/{path_hex} fehlgeschlagen: {err}"
                ) from err

        data = _extract_data(payload)
        if data is None:
            raise JudoApiError(
                f"Keine 'data'-Angabe in /api/rest/{path_hex}: {payload!r}"
            )
        if isinstance(data, str):
            return data.strip().replace(" ", "").upper()
        if isinstance(data, (int, float)):
            return str(data)
        raise JudoApiError(
            f"Unerwarteter Datentyp für /api/rest/{path_hex}: {type(data).__name__}"
        )

    async def read(self, command: str) -> str:
        """Read one command, adding the required 00 read marker."""
        command = command.upper()
        if command == "6900":
            return await self.request("6900")
        if len(command) != 2:
            raise JudoApiError(f"Ungültiger Lese-Befehl: {command}")
        return await self.request(f"{command}00")

    async def write(self, command: str, data_hex: str = "") -> str:
        """Write command + 00 + data and return the response data.

        For zero-data commands (3C/3D), this still generates e.g. 3C00.
        """
        command = command.upper()
        data_hex = data_hex.replace(" ", "").strip().upper()
        if len(command) != 2 or len(data_hex) % 2:
            raise JudoApiError(f"Ungültiger Schreib-Befehl: {command}{data_hex}")
        return await self.request(f"{command}00{data_hex}")

    async def test_connection(self) -> None:
        """Use the device type command as connection test."""
        await self.read("FF")


def _extract_data(payload: Any) -> Any:
    """Extract JUDO's data property from common response wrappers."""
    if isinstance(payload, dict):
        if "data" in payload:
            return payload["data"]
        for value in payload.values():
            found = _extract_data(value)
            if found is not None:
                return found
    elif isinstance(payload, Iterable) and not isinstance(
        payload, (str, bytes, bytearray)
    ):
        for item in payload:
            found = _extract_data(item)
            if found is not None:
                return found
    return None

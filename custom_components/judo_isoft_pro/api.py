"""Gemeinsame REST-Kommunikation mit einer globalen Ratebegrenzung."""
import logging
import threading
import time
import requests
from requests.auth import HTTPBasicAuth

_LOGGER = logging.getLogger(__name__)

# Global für die komplette Integration:
# Zwischen zwei HTTP-Kommandos liegen mindestens 1,0 s.
_RATE_LOCK = threading.Lock()
_NEXT_REQUEST_AT = 0.0
_MIN_INTERVAL = 1.0


def _wait_for_rate_limit() -> None:
    """Wartet so lange, dass maximal ein REST-Kommando pro Sekunde startet."""
    global _NEXT_REQUEST_AT

    with _RATE_LOCK:
        now = time.monotonic()
        wait = max(0.0, _NEXT_REQUEST_AT - now)
        if wait:
            time.sleep(wait)

        # Zeitpunkt des nächsten erlaubten Requests reservieren.
        _NEXT_REQUEST_AT = time.monotonic() + _MIN_INTERVAL


def request(method: str, ip: str, user: str, password: str, command: str, timeout: float = 10.0):
    """Führt einen GET/POST auf der Anlage aus und begrenzt die Rate global."""
    _wait_for_rate_limit()

    url = f"http://{ip}/api/rest/{command}"
    return requests.request(
        method,
        url,
        auth=HTTPBasicAuth(user, password),
        timeout=timeout,
    )

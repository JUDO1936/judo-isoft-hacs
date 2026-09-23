"""Constants for the JUDO i-soft PRO / PRO L integration."""

from __future__ import annotations

import re
from datetime import timedelta

DOMAIN = "judo_isoft_pro"
INTEGRATION_NAME = "JUDO i-soft PRO / PRO L"

# Config Flow / Config Entry
CONF_NAME = "name"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_DEVICE_ID = "device_id"

DEFAULT_PORT = 80
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "Connectivity"
DEFAULT_TIMEOUT = 10.0

POLL_INTERVAL = timedelta(minutes=10)
RECHECK_DELAY = 5.0

# Maximal ein Kommando pro Sekunde und Gerät.
MIN_COMMAND_INTERVAL = 1.0

MAX_REQUEST_RETRIES = 1
RETRY_DELAY = 0.2


# ---------------------------------------------------------------------------
# JUDO i-soft PRO / PRO L REST commands
# ---------------------------------------------------------------------------

CMD_HARDNESS = "51"
CMD_HARDNESS_UNIT_READ = "23"
CMD_HARDNESS_WRITE = "30"
CMD_HARDNESS_UNIT_WRITE = "24"

CMD_SALT = "56"
CMD_SALT_WARNING = "57"

CMD_MAX_DRAW_TIME = "3E"
CMD_MAX_DRAW_AMOUNT = "3F"
CMD_MAX_FLOW = "40"

CMD_LEAK_CLOSE = "3C"
CMD_LEAK_OPEN = "3D"

CMD_REGENERATION = "35"
CMD_SCENE = "36"

CMD_TOTAL_WATER = "28"
CMD_SOFTENED_WATER = "29"

CMD_DEVICE_TYPE = "FF"
CMD_DEVICE_NUMBER = "06"
CMD_SOFTWARE_VERSION = "01"
CMD_OPERATING_HOURS = "25"

CMD_6900_READ = "6900"


# ---------------------------------------------------------------------------
# Polling
# ---------------------------------------------------------------------------

# Die Abfragen werden absichtlich nacheinander ausgeführt.
# Pro Gerät wird maximal ein Kommando pro Sekunde gestartet.
POLL_COMMANDS = (
    CMD_DEVICE_TYPE,
    CMD_DEVICE_NUMBER,
    CMD_SOFTWARE_VERSION,
    CMD_HARDNESS,
    CMD_HARDNESS_UNIT_READ,
    CMD_SALT,
    CMD_SALT_WARNING,
    CMD_MAX_DRAW_TIME,
    CMD_MAX_DRAW_AMOUNT,
    CMD_MAX_FLOW,
    CMD_TOTAL_WATER,
    CMD_SOFTENED_WATER,
    CMD_OPERATING_HOURS,
    CMD_6900_READ,
)


RECHECKABLE_COMMANDS = frozenset(
    {
        CMD_HARDNESS,
        CMD_HARDNESS_UNIT_READ,
        CMD_SALT,
        CMD_SALT_WARNING,
        CMD_MAX_DRAW_TIME,
        CMD_MAX_DRAW_AMOUNT,
        CMD_MAX_FLOW,
    }
)


# ---------------------------------------------------------------------------
# JUDO Gerätetypen
# ---------------------------------------------------------------------------

# Werte aus der JUDO REST-API-Dokumentation:
#
# 0x58 = i-soft PRO
# 0x4B = i-soft PRO
# 0x4C = i-soft PRO L

DEVICE_TYPES = {
    0x58: "i-soft PRO",
    0x4B: "i-soft PRO",
    0x4C: "i-soft PRO L",
}


# ---------------------------------------------------------------------------
# Wasserhärteeinheiten
# ---------------------------------------------------------------------------

HARDNESS_UNIT_OPTIONS = {
    "0": "°dH",
    "1": "°eH",
    "2": "°fH",
    "3": "gpg",
    "4": "ppm",
    "5": "mmol",
    "6": "mval",
}


# ---------------------------------------------------------------------------
# Szenen
# ---------------------------------------------------------------------------

SCENE_OPTIONS = {
    "0": "Alltag meistern",
    "1": "Körper pflegen",
    "2": "Garten bewässern",
    "3": "Urlaub genießen",
    "4": "Wäsche waschen",
    "5": "Hochdruckreinigen",
    "6": "Pool befüllen",
    "7": "Heizung befüllen",
    "8": "Custom Szene 1",
    "9": "Custom Szene 2",
    "A": "Custom Szene 3",
}


# ---------------------------------------------------------------------------
# Szenendauer
# ---------------------------------------------------------------------------

SCENE_DURATION_OPTIONS = {
    "000F": "00:15",
    "001E": "00:30",
    "002D": "00:45",
    "0100": "01:00",
    "0200": "02:00",
    "0600": "06:00",
    "0C00": "12:00",
    "FFFF": "Unbegrenzt",
}


SCENE_NAME_TO_CODE = {
    name: code
    for code, name in SCENE_OPTIONS.items()
}


SCENE_DURATION_NAME_TO_CODE = {
    name: code
    for code, name in SCENE_DURATION_OPTIONS.items()
}


HARDNESS_UNIT_NAME_TO_CODE = {
    name: code
    for code, name in HARDNESS_UNIT_OPTIONS.items()
}


# ---------------------------------------------------------------------------
# 6900 – Leckageschutz
# ---------------------------------------------------------------------------

# Byte 2 der 6900-Antwort.
LEAKAGE_STATUS_BITS = {
    0x01: "Volumenstrom",
    0x02: "Menge",
    0x04: "Zeit",
    0x08: "Mikroleckageprüfung",
    0x10: "Schließen bei Mikroleckage",
    0x20: "Externe Sensoren",
}


# Byte 3 der 6900-Antwort.
LEAKAGE_REASON_BITS = {
    0x01: "Volumenstrom überschritten",
    0x02: "Menge überschritten",
    0x04: "Zeit überschritten",
    0x08: "Externer Kabelsensor",
    0x10: "Manuell geschlossen",
    0x20: "Manuelle Mikroleckage",
    0x40: "Automatische Mikroleckage",
    0x80: "Homeguard-Meldung",
}


# ---------------------------------------------------------------------------
# Entity-ID Präfix
# ---------------------------------------------------------------------------

def entity_prefix(host: str, port: int) -> str:
    """Create a stable entity-id prefix from the configured endpoint."""

    slug = re.sub(
        r"[^a-z0-9]+",
        "_",
        host.lower(),
    ).strip("_") or "geraet"

    if port != DEFAULT_PORT:
        slug = f"{slug}_p{port}"

    return f"{DOMAIN}_{slug}"

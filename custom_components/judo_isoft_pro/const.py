"""Constants for the JUDO i-soft PRO / PRO L Home Assistant integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "judo_isoft_pro"
INTEGRATION_NAME = "JUDO i-soft PRO / PRO L"

DEFAULT_PORT = 80
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "Connectivity"
DEFAULT_TIMEOUT = 10.0
POLL_INTERVAL = timedelta(minutes=10)
RECHECK_DELAY = 5.0
MIN_COMMAND_INTERVAL = 1.0

CONF_HOST = "host"
CONF_PORT = "port"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# JUDO i-soft PRO / PRO L REST commands.
# A read request is COMMAND + 00, e.g. 5100.
# A write request is COMMAND + 00 + DATA, e.g. 300007.
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
CMD_COMMISSIONING_DATE = "0E"
CMD_OPERATING_HOURS = "25"

# Requested future command. It is already polled and decoded generically so it
# never blocks the documented PRO commands if a device does not support it yet.
CMD_6900 = "69"
CMD_6900_READ = "6900"

POLL_COMMANDS = (
    CMD_HARDNESS,
    CMD_HARDNESS_UNIT_READ,
    CMD_SALT,
    CMD_SALT_WARNING,
    CMD_MAX_DRAW_TIME,
    CMD_MAX_DRAW_AMOUNT,
    CMD_MAX_FLOW,
    CMD_TOTAL_WATER,
    CMD_SOFTENED_WATER,
    CMD_DEVICE_TYPE,
    CMD_SOFTWARE_VERSION,
    CMD_COMMISSIONING_DATE,
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

# Device type values documented by JUDO for the i-soft PRO family.
DEVICE_TYPES = {
    0x58: "i-soft PRO",
    0x4B: "i-soft PRO",
    0x4C: "i-soft PRO L",
}

# For the PRO / PRO L documentation only these two units are specified.
HARDNESS_UNIT_OPTIONS = {
    "0": "°dH",
    "2": "°fH",
}

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

SCENE_NAME_TO_CODE = {name: code for code, name in SCENE_OPTIONS.items()}
SCENE_DURATION_NAME_TO_CODE = {
    name: code for code, name in SCENE_DURATION_OPTIONS.items()
}
HARDNESS_UNIT_NAME_TO_CODE = {
    name: code for code, name in HARDNESS_UNIT_OPTIONS.items()
}

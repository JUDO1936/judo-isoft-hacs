"""Pure protocol decoding helpers for the JUDO i-soft PRO API."""

from __future__ import annotations

from dataclasses import dataclass

from .const import LEAKAGE_REASON_BITS, LEAKAGE_STATUS_BITS, SCENE_OPTIONS


@dataclass(frozen=True, slots=True)
class Judo6900Status:
    """Decoded fields from the JUDO PRO 6900/69 status response."""

    active_scene: int
    active_scene_options: int
    leakage_status: int
    leakage_reason: int
    current_water_flow_l_h: int
    current_draw_duration_min: int
    current_water_amount_l: int
    current_water_temperature_c: int


def decode_6900(raw_hex: str | None) -> Judo6900Status | None:
    """Decode the documented PRO 6900 status layout.

    The API document specifies 16 response bytes. We only require the first
    12 bytes because the requested dashboard values end at byte 11; the two
    final pairs are documented as unused.
    """
    if not raw_hex:
        return None
    try:
        data = bytes.fromhex(raw_hex)
    except ValueError:
        return None
    if len(data) < 12:
        return None

    return Judo6900Status(
        active_scene=data[0],
        active_scene_options=data[1],
        leakage_status=data[2],
        leakage_reason=data[3],
        current_water_flow_l_h=int.from_bytes(data[4:6], "little"),
        current_draw_duration_min=int.from_bytes(data[6:8], "little"),
        current_water_amount_l=int.from_bytes(data[8:10], "little"),
        current_water_temperature_c=int.from_bytes(data[10:12], "little"),
    )


def scene_label(code: int) -> str:
    """Return the human-readable name of a scene code."""
    key = f"{code:X}"
    return SCENE_OPTIONS.get(key, f"Unbekannte Szene 0x{code:02X}")


def leakage_status_label(value: int) -> str:
    """Return a concise global leakage-protection status."""
    if value == 0:
        return "Deaktiviert"
    active = [name for bit, name in LEAKAGE_STATUS_BITS.items() if value & bit]
    return "Aktiv" if not active else f"Aktiv – {', '.join(active)}"


def leakage_status_details(value: int) -> list[str]:
    """Return the active leakage-protection functions."""
    if value == 0:
        return []
    return [name for bit, name in LEAKAGE_STATUS_BITS.items() if value & bit]


def leakage_reason_label(value: int) -> str:
    """Return a human-readable leakage reason."""
    if value == 0:
        return "Keine Leckage"
    reasons = [name for bit, name in LEAKAGE_REASON_BITS.items() if value & bit]
    return ", ".join(reasons) if reasons else f"Unbekannter Grund 0x{value:02X}"

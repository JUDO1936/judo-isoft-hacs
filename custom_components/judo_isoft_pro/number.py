"""Number-Plattform für JUDO i-soft PRO / L."""
import logging

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import request
from .const import (
    DOMAIN,
    CONF_IP_ADDRESS,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_DEVICE_NAME,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Erstellt alle Number-Entitäten für eine JUDO i-soft PRO Anlage."""
    config = entry.data
    ip = config[CONF_IP_ADDRESS]
    user = config[CONF_USERNAME]
    pwd = config[CONF_PASSWORD]
    device_name = config.get(CONF_DEVICE_NAME) or f"JUDO i-soft PRO ({ip})"

    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=device_name,
        manufacturer="JUDO",
        model="i-soft PRO / L",
        configuration_url=f"http://{ip}",
    )

    numbers = [
        JudoHardnessNumber(entry, device_info, ip, user, pwd),
        JudoMaxVolumeNumber(entry, device_info, ip, user, pwd),
        JudoMaxFlowNumber(entry, device_info, ip, user, pwd),
        JudoHolidayDaysNumber(entry, device_info, ip, user, pwd),
    ]

    async_add_entities(numbers, True)


class JudoBaseNumber(NumberEntity):
    """Basissklasse für JUDO Number-Entitäten."""

    def __init__(self, entry, device_info, ip, user, pwd, name, unique_key, min_val, max_val, step, unit, icon, initial):
        self._entry = entry
        self._ip = ip
        self._user = user
        self._pwd = pwd
        self._attr_name = f"i-soft PRO {name}"
        self._attr_unique_id = f"judo_isoft_pro_{entry.entry_id}_{unique_key}"
        self._attr_device_info = device_info
        self._attr_native_min_value = min_val
        self._attr_native_max_value = max_val
        self._attr_native_step = step
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._value = initial

    @property
    def native_value(self) -> float:
        return self._value


class JudoHardnessNumber(JudoBaseNumber):
    """Einstellung der Wunschwasserhärte (1 - 30 °dH)."""

    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(
            entry, device_info, ip, user, pwd,
            name="Wunschwasserhärte Einstellen",
            unique_key="set_wunschwasserhaerte",
            min_val=1, max_val=30, step=1,
            unit="°dH", icon="mdi:water-softener", initial=8
        )

    async def async_set_native_value(self, value: float) -> None:
        target = int(value)
        command = f"3000{target:02X}"
        try:
            await self.hass.async_add_executor_job(
                request, "POST", self._ip, self._user, self._pwd, command, 10.0
            )
            self._value = target
            self.async_write_ha_state()
        except Exception as err:
            _LOGGER.error("Fehler beim Setzen der Wunschwasserhärte: %s", err)


class JudoMaxVolumeNumber(JudoBaseNumber):
    """Einstellung der maximalen Entnahmemenge (100 - 3000 Liter)."""

    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(
            entry, device_info, ip, user, pwd,
            name="Max. Entnahmemenge Einstellen",
            unique_key="set_max_volume",
            min_val=100, max_val=3000, step=50,
            unit="L", icon="mdi:water-minus", initial=1000
        )

    async def async_set_native_value(self, value: float) -> None:
        target = int(value)
        lsb = target % 256
        msb = target // 256
        command = f"3F00{lsb:02X}{msb:02X}"
        try:
            await self.hass.async_add_executor_job(
                request, "POST", self._ip, self._user, self._pwd, command, 10.0
            )
            self._value = target
            self.async_write_ha_state()
        except Exception as err:
            _LOGGER.error("Fehler beim Setzen der max. Entnahmemenge: %s", err)


class JudoMaxFlowNumber(JudoBaseNumber):
    """Einstellung des maximalen Volumenstroms (500 - 5000 L/h)."""

    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(
            entry, device_info, ip, user, pwd,
            name="Max. Volumenstrom Einstellen",
            unique_key="set_max_flow",
            min_val=500, max_val=5000, step=100,
            unit="L/h", icon="mdi:speedometer", initial=2000
        )

    async def async_set_native_value(self, value: float) -> None:
        target = int(value)
        lsb = target % 256
        msb = target // 256
        command = f"4000{lsb:02X}{msb:02X}"
        try:
            await self.hass.async_add_executor_job(
                request, "POST", self._ip, self._user, self._pwd, command, 10.0
            )
            self._value = target
            self.async_write_ha_state()
        except Exception as err:
            _LOGGER.error("Fehler beim Setzen des max. Volumenstroms: %s", err)


class JudoHolidayDaysNumber(JudoBaseNumber):
    """Setzen der Urlaubsmodus-Dauer in Tagen (1 - 30 Tage)."""

    def __init__(self, entry, device_info, ip, user, pwd):
        super().__init__(
            entry, device_info, ip, user, pwd,
            name="Urlaubsmodus Dauer",
            unique_key="set_holiday_days",
            min_val=1, max_val=30, step=1,
            unit="Tage", icon="mdi:calendar-range", initial=7
        )

    async def async_set_native_value(self, value: float) -> None:
        target = int(value)
        command = f"410001{target:02X}"
        try:
            await self.hass.async_add_executor_job(
                request, "POST", self._ip, self._user, self._pwd, command, 10.0
            )
            self._value = target
            self.async_write_ha_state()
        except Exception as err:
            _LOGGER.error("Fehler beim Starten des Urlaubsmodus: %s", err)

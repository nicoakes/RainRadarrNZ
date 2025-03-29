# File: /custom_components/rainradar/__init__.py

from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery
from homeassistant.config_entries import ConfigEntry

DOMAIN = "rainradar"

async def async_setup(hass: HomeAssistant, config: dict):
    hass.data[DOMAIN] = {}
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data[DOMAIN][entry.entry_id] = entry.data
    await discovery.async_load_platform(hass, "sensor", DOMAIN, {}, entry)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await discovery.async_unload_platform(hass, "sensor", DOMAIN)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
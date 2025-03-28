from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import CONF_NAME
import logging
import requests
import os
from datetime import datetime, timedelta
import pytz

_LOGGER = logging.getLogger(__name__)

class RainRadarSensor(Entity):
    def __init__(self, coordinator: DataUpdateCoordinator, name: str):
        self.coordinator = coordinator
        self._name = name
        self._image_url = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._image_url

    async def async_update(self):
        await self.coordinator.async_request_refresh()

class RainRadarDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, base_url, timezone):
        super().__init__(hass, _LOGGER, name="Rain Radar Data")
        self.base_url = base_url
        self.timezone = pytz.timezone(timezone)

    async def _async_update_data(self):
        now = datetime.now(self.timezone)
        offset = "+13:00" if now.dst() else "+12:00"
        urls = []

        for i in range(60):
            time_check = now - timedelta(minutes=i)
            timestamp = time_check.strftime("%Y-%m-%dT%H:%M:00")
            urls.append(f"{self.base_url}{timestamp}{offset}")

        return urls

async def async_setup_entry(hass, entry):
    base_url = entry.data[CONF_NAME]
    timezone = "Pacific/Auckland"  # You can make this configurable if needed

    coordinator = RainRadarDataUpdateCoordinator(hass, base_url, timezone)
    await coordinator.async_refresh()

    hass.data.setdefault("rainradar", {})
    hass.data["rainradar"]["coordinator"] = coordinator

    hass.helpers.discovery.load_platform("sensor", "rainradar", {}, entry)
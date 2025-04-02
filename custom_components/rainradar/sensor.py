from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import CONF_NAME
import logging
import requests
import os
from datetime import datetime, timedelta
import pytz
import re  # Import regex for parsing timestamps from filenames

_LOGGER = logging.getLogger(__name__)

IMAGE_DIR = "www/rainradar_images"
IMAGE_TIMESTAMP_FORMAT = "%Y-%m-%dT%H-%M"  # Format used in image filenames

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

async def delete_old_images(hass):
    """Delete images older than 2 hours based on the timestamp in the filename."""
    image_path = hass.config.path(IMAGE_DIR)
    now = datetime.now()

    def cleanup():
        for filename in os.listdir(image_path):
            if filename.endswith(".gif"):
                # Extract timestamp from the filename
                match = re.search(r"rain_radar_(\d{4}-\d{2}-\d{2}T\d{2}-\d{2})\.gif", filename)
                if match:
                    timestamp_str = match.group(1)
                    try:
                        file_time = datetime.strptime(timestamp_str, IMAGE_TIMESTAMP_FORMAT)
                        # Check if the file is older than 2 hours
                        if now - file_time > timedelta(hours=2):
                            os.remove(os.path.join(image_path, filename))
                            _LOGGER.info(f"Deleted old image: {filename}")
                    except ValueError:
                        _LOGGER.warning(f"Invalid timestamp in filename: {filename}")

    # Run the cleanup in a thread-safe manner
    await hass.async_add_executor_job(cleanup)

async def async_setup_entry(hass, entry):
    base_url = entry.data[CONF_NAME]
    timezone = "Pacific/Auckland"  # You can make this configurable if needed

    coordinator = RainRadarDataUpdateCoordinator(hass, base_url, timezone)
    await coordinator.async_refresh()

    hass.data.setdefault("rainradar", {})
    hass.data["rainradar"]["coordinator"] = coordinator

    # Schedule periodic cleanup of old images
    async def periodic_cleanup():
        while True:
            await delete_old_images(hass)
            await asyncio.sleep(3600)  # Run cleanup every hour

    hass.loop.create_task(periodic_cleanup())

    hass.helpers.discovery.load_platform("sensor", "rainradar", {}, entry)
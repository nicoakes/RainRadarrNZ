import os
import asyncio
from datetime import datetime, timedelta
import aiohttp
import pytz
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery

DOMAIN = "rainradar"
IMAGE_DIR = "www/rainradar_images"
BASE_URL = "https://www.metservice.com/publicData/rainRadar/image/Christchurch/300K/"
TIMEZONE = "Pacific/Auckland"
DOWNLOAD_INTERVAL = 8 * 60  # 8 minutes

_LOGGER = logging.getLogger(__name__)  # Use this logger for logging messages

def get_timezone():
    """Get the timezone object in a synchronous context."""
    return pytz.timezone(TIMEZONE)

def write_file(filename, content):
    """Write content to a file in a thread-safe way."""
    with open(filename, 'wb') as file:
        file.write(content)

async def download_images(hass: HomeAssistant):
    """Download radar images periodically."""
    # Get the timezone in a thread-safe way
    tz = await hass.async_add_executor_job(get_timezone)
    os.makedirs(hass.config.path(IMAGE_DIR), exist_ok=True)

    async with aiohttp.ClientSession() as session:
        while True:
            now = datetime.now(tz)
            offset = "+13:00" if now.dst() else "+12:00"
            urls = []
            for i in range(60):
                time_check = now - timedelta(minutes=i)
                timestamp = time_check.strftime("%Y-%m-%dT%H:%M:00")
                urls.append((time_check, f"{BASE_URL}{timestamp}{offset}"))

            for timestamp, url in urls:
                filename = os.path.join(hass.config.path(IMAGE_DIR), f"rain_radar_{timestamp.strftime('%Y-%m-%dT%H-%M')}.gif")
                if not os.path.exists(filename):
                    try:
                        async with session.get(url) as response:
                            if response.status == 200:
                                content = await response.read()
                                await hass.async_add_executor_job(write_file, filename, content)
                                _LOGGER.info(f"Downloaded: {filename}")  # Use _LOGGER for logging
                            else:
                                _LOGGER.debug(f"Not found: {url}")  # Use _LOGGER for logging
                    except Exception as e:
                        _LOGGER.error(f"Error downloading {url}: {e}")  # Use _LOGGER for logging

            await asyncio.sleep(DOWNLOAD_INTERVAL)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Rain Radar integration."""
    hass.loop.create_task(download_images(hass))
    await discovery.async_load_platform(hass, "camera", DOMAIN, {}, config)
    return True
import os
import asyncio
from datetime import datetime, timedelta
import aiohttp
import pytz
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery
from PIL import Image  # Add this import for image cropping

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

def crop_image(filename, crop_box):
    """Crop the image to the specified box."""
    with Image.open(filename) as img:
        cropped = img.crop(crop_box)
        cropped.save(filename)

async def download_images(hass: HomeAssistant):
    """Download radar images periodically."""
    # Get the timezone in a thread-safe way
    tz = await hass.async_add_executor_job(get_timezone)
    os.makedirs(hass.config.path(IMAGE_DIR), exist_ok=True)

    # Get crop box from configuration
    crop_box = hass.data[DOMAIN].get("crop_box", (240, 200, 1030, 850))

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
                                # Crop the image in a non-blocking manner
                                await hass.async_add_executor_job(crop_image, filename, crop_box)
                                _LOGGER.info(f"Downloaded and cropped: {filename}")  # Use _LOGGER for logging
                            else:
                                _LOGGER.debug(f"Not found: {url}")  # Use _LOGGER for logging
                    except Exception as e:
                        _LOGGER.error(f"Error downloading {url}: {e}")  # Use _LOGGER for logging

            await asyncio.sleep(DOWNLOAD_INTERVAL)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Rain Radar integration."""
    # Load crop box and image limit configuration
    crop_box = config.get(DOMAIN, {}).get("crop_box", (240, 200, 1030, 850))
    image_limit = config.get(DOMAIN, {}).get("image_limit", 6)  # Default to 6 images
    hass.data[DOMAIN] = {"crop_box": crop_box, "image_limit": image_limit}

    hass.loop.create_task(download_images(hass))
    await discovery.async_load_platform(hass, "camera", DOMAIN, {}, config)
    return True
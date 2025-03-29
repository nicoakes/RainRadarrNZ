import os
import asyncio
from datetime import datetime, timedelta
import requests
import pytz
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery
from homeassistant.util.async_ import run_callback_threadsafe

DOMAIN = "rainradar"
IMAGE_DIR = "www/rainradar_images"
BASE_URL = "https://www.metservice.com/publicData/rainRadar/image/Christchurch/300K/"
TIMEZONE = "Pacific/Auckland"
DOWNLOAD_INTERVAL = 8 * 60  # 8 minutes

def get_timezone():
    """Get the timezone object in a synchronous context."""
    return pytz.timezone(TIMEZONE)

async def download_images(hass: HomeAssistant):
    """Download radar images periodically."""
    # Get the timezone in a thread-safe way
    tz = await hass.async_add_executor_job(get_timezone)
    os.makedirs(hass.config.path(IMAGE_DIR), exist_ok=True)

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
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    with open(filename, 'wb') as file:
                        for chunk in response.iter_content(1024):
                            file.write(chunk)
                    hass.logger.info(f"Downloaded: {filename}")
                else:
                    hass.logger.debug(f"Not found: {url}")

        await asyncio.sleep(DOWNLOAD_INTERVAL)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Rain Radar integration."""
    hass.loop.create_task(download_images(hass))
    await discovery.async_load_platform(hass, "camera", DOMAIN, {}, config)
    return True
import os
import asyncio  # Import asyncio for pausing
from homeassistant.components.camera import Camera
from homeassistant.core import HomeAssistant

DOMAIN = "rainradar"
IMAGE_DIR = "www/rainradar_images"
DEFAULT_IMAGE_LIMIT = 6  # Default number of images to display
DEFAULT_PAUSE_SECONDS = 3  # Default pause duration on the last image

async def async_setup_platform(hass: HomeAssistant, config, async_add_entities, discovery_info=None):
    """Set up the Rain Radar camera."""
    # Get the image limit and pause duration from configuration or use defaults
    image_limit = hass.data[DOMAIN].get("image_limit", DEFAULT_IMAGE_LIMIT)
    pause_seconds = hass.data[DOMAIN].get("pause_seconds", DEFAULT_PAUSE_SECONDS)
    async_add_entities([RainRadarCamera(hass, image_limit, pause_seconds)])

class RainRadarCamera(Camera):
    """Rain Radar Camera Entity."""

    def __init__(self, hass: HomeAssistant, image_limit: int, pause_seconds: int):
        """Initialize the camera."""
        super().__init__()
        self.hass = hass
        self.image_files = []
        self.current_index = 0
        self.image_limit = image_limit
        self.pause_seconds = pause_seconds
        self.pause_on_last_image = False

    async def update_image_list(self):
        """Update the list of image files asynchronously."""
        image_path = self.hass.config.path(IMAGE_DIR)
        self.image_files = await self.hass.async_add_executor_job(
            lambda: sorted(
                [os.path.join(image_path, f) for f in os.listdir(image_path) if f.endswith(".gif")]
            )[-self.image_limit:]  # Limit to the last X images
        )

    async def async_camera_image(self):
        """Return the current image asynchronously."""
        await self.update_image_list()
        if not self.image_files:
            return None

        # Check if we are on the last image
        if self.current_index == len(self.image_files) - 1:
            if not self.pause_on_last_image:
                self.pause_on_last_image = True
                await asyncio.sleep(self.pause_seconds)  # Pause for the configured duration
            else:
                self.pause_on_last_image = False

        # Loop through images
        self.current_index = (self.current_index + 1) % len(self.image_files)
        with open(self.image_files[self.current_index], "rb") as file:
            return file.read()

    @property
    def name(self):
        """Return the name of the camera."""
        return "Rain Radar"
import os
from homeassistant.components.camera import Camera
from homeassistant.core import HomeAssistant

DOMAIN = "rainradar"
IMAGE_DIR = "www/rainradar_images"

async def async_setup_platform(hass: HomeAssistant, config, async_add_entities, discovery_info=None):
    """Set up the Rain Radar camera."""
    async_add_entities([RainRadarCamera(hass)])

class RainRadarCamera(Camera):
    """Rain Radar Camera Entity."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the camera."""
        super().__init__()
        self.hass = hass
        self.image_files = []
        self.current_index = 0

    async def update_image_list(self):
        """Update the list of image files asynchronously."""
        image_path = self.hass.config.path(IMAGE_DIR)
        self.image_files = await self.hass.async_add_executor_job(
            lambda: sorted(
                [os.path.join(image_path, f) for f in os.listdir(image_path) if f.endswith(".gif")]
            )
        )

    async def async_camera_image(self):
        """Return the current image asynchronously."""
        await self.update_image_list()
        if not self.image_files:
            return None

        # Loop through images
        self.current_index = (self.current_index + 1) % len(self.image_files)
        with open(self.image_files[self.current_index], "rb") as file:
            return file.read()

    @property
    def name(self):
        """Return the name of the camera."""
        return "Rain Radar"
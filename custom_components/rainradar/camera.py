import os
import asyncio
import re
from datetime import datetime
from homeassistant.components.camera import Camera
from homeassistant.core import HomeAssistant
from PIL import Image, ImageDraw, ImageFont  # Import Pillow for image manipulation
import io

DOMAIN = "rainradar"
IMAGE_DIR = "www/rainradar_images"
DEFAULT_IMAGE_LIMIT = 6  # Default number of images to display
DEFAULT_PAUSE_SECONDS = 3  # Default pause duration on the last image
IMAGE_TIMESTAMP_FORMAT = "%Y-%m-%dT%H-%M"  # Format used in image filenames

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

        def get_sorted_images():
            """Retrieve and sort image files by timestamp."""
            images = []
            for filename in os.listdir(image_path):
                if filename.endswith(".gif"):
                    match = re.search(r"rain_radar_(\d{4}-\d{2}-\d{2}T\d{2}-\d{2})\.gif", filename)
                    if match:
                        timestamp_str = match.group(1)
                        try:
                            timestamp = datetime.strptime(timestamp_str, IMAGE_TIMESTAMP_FORMAT)
                            images.append((timestamp, os.path.join(image_path, filename)))
                        except ValueError:
                            continue
            # Sort images by timestamp and return the most recent ones
            return [file for _, file in sorted(images)[-self.image_limit:]]

        self.image_files = await self.hass.async_add_executor_job(get_sorted_images)

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

        # Add timestamp to the image in a thread-safe, non-blocking manner
        def add_timestamp_to_image(file_path):
            """Add a timestamp to the bottom-left corner of the image."""
            with Image.open(file_path) as img:
                draw = ImageDraw.Draw(img)
                # Extract timestamp from the filename
                match = re.search(r"rain_radar_(\d{4}-\d{2}-\d{2}T\d{2}-\d{2})\.gif", file_path)
                if match:
                    timestamp_str = match.group(1)
                else:
                    timestamp_str = "Unknown Timestamp"

                # Define font and text properties
                font_path = os.path.join(os.path.dirname(__file__), "arial.ttf")  # Path to a .ttf font file
                font_size = 20  # Set font size (twice the default size)
                font = ImageFont.truetype(font_path, font_size)
                padding = 5

                # Calculate text size using textbbox
                text_bbox = draw.textbbox((0, 0), timestamp_str, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]

                # Define text position
                text_position = (padding, img.height - text_height - padding)

                # Draw white rectangle as background for the text
                draw.rectangle(
                    [text_position, (text_position[0] + text_width + padding, text_position[1] + text_height + padding)],
                    fill="white"
                )
                # Draw the timestamp text in black
                draw.text(text_position, timestamp_str, fill="black", font=font)

                # Save the modified image to a temporary buffer
                output = io.BytesIO()
                img.save(output, format="GIF")
                return output.getvalue()

        return await self.hass.async_add_executor_job(add_timestamp_to_image, self.image_files[self.current_index])

    @property
    def name(self):
        """Return the name of the camera."""
        return "Rain Radar"
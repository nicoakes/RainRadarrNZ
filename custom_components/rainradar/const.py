# Constants for the RainRadar Home Assistant integration

DOMAIN = "rainradar"
CONF_BASE_URL = "base_url"
CONF_IMAGE_DIR = "image_dir"
DEFAULT_BASE_URL = "https://www.metservice.com/publicData/rainRadar/image/Christchurch/300K/"
DEFAULT_IMAGE_DIR = "images"
SCAN_INTERVAL = 480  # Time in seconds to scan for new images

# Image file naming format
IMAGE_FILENAME_FORMAT = "rain_radar_{timestamp}.gif"
# RainRadar Home Assistant Integration

## Overview
The RainRadar integration for Home Assistant allows users to fetch and display rain radar images from MetService. This integration automatically downloads the latest images and provides them as sensor entities that can be displayed on the Home Assistant dashboard.

## Installation
1. Clone this repository or download the files.
2. Place the `rainradar` folder in your Home Assistant `custom_components` directory.
3. Restart Home Assistant.

## Configuration
To configure the RainRadar integration, follow these steps:

1. Go to the Home Assistant UI.
2. Navigate to **Configuration** > **Integrations**.
3. Click on **Add Integration** and search for **RainRadar**.
4. Follow the prompts to complete the setup.

5. 2. Add the Integration to configuration.yaml
If your integration does not support UI-based configuration, you can configure it manually in the configuration.yaml file. Based on the constants in your const.py, the configuration might look like this:

base_url: The URL to fetch radar images.
image_dir: The directory where radar images will be saved.

### Configuration Options
- **Base URL**: The URL from which to fetch the rain radar images. Default is `https://www.metservice.com/publicData/rainRadar/image/Christchurch/300K/`.
- **Timezone**: The timezone to use for timestamps. Default is `Pacific/Auckland`.
- **Hang Time**: The duration (in seconds) to display the latest image before fetching a new one. Default is `5`.

## Usage
Once configured, the RainRadar integration will create sensor entities that represent the latest rain radar images. You can add these sensors to your dashboard to view the images.

### Example
To display the rain radar images on your dashboard, you can use the following configuration in your `ui-lovelace.yaml`:

```yaml
type: picture-entity
entity: sensor.rain_radar
```

## Troubleshooting
- Ensure that the `custom_components` directory is correctly set up in your Home Assistant configuration.
- Check the Home Assistant logs for any errors related to the RainRadar integration.
- Verify that the base URL is accessible and returns valid images.

## Contributing
If you would like to contribute to the RainRadar integration, feel free to submit a pull request or open an issue for any bugs or feature requests.

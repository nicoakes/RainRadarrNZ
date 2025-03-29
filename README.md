# RainRadar Home Assistant Integration

## Overview
The RainRadar integration for Home Assistant allows users to fetch and display rain radar images from MetService. This integration automatically downloads the latest images and provides them as sensor entities that can be displayed on the Home Assistant dashboard.

## Installation
1. Clone this repository or download the files.
2. Place the `rainradar` folder in your Home Assistant `custom_components` directory.
3. Restart Home Assistant.

## Configuration
To configure the RainRadar integration, follow these steps:

1. Add the Integration to configuration.yaml

```yaml
rainradar:
  base_url: "https://www.metservice.com/publicData/rainRadar/image/Christchurch/300K/"
  image_dir: "images"
```
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

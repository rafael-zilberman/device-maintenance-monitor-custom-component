# Device Maintenance Monitor

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/docs/faq/custom_repositories)

A custom Home Assistant integration to monitor the maintenance of any device. It supports three types of maintenance monitors: Runtime, Power On Count, and Fixed Interval.

## Features

- Track the last maintenance date.
- Monitor total runtime hours, power on count, or fixed interval depending on the type of monitor.
- Calculate remaining hours or counts until the device needs maintenance.
- Provide a boolean sensor indicating if the device needs maintenance.
- Include a button to reset the maintenance data.

## Installation

### Manual Installation

1. Download the `device_maintenance_monitor` directory from the [latest release](https://github.com/your_github_username/device_maintenance_monitor/releases/latest).
2. Copy the `device_maintenance_monitor` directory to your `custom_components` directory in your Home Assistant configuration directory.

### HACS Installation

1. Open Home Assistant and go to HACS.
2. Click on "Integrations" and then the three dots in the top right corner.
3. Select "Custom repositories".
4. Add the repository URL: `https://github.com/your_github_username/device_maintenance_monitor` and select the category as "Integration".
5. Find "Device Maintenance Monitor" in the HACS store and install it.

## Configuration

1. After installation, go to Home Assistant and navigate to `Configuration` -> `Integrations`.
2. Click on `Add Integration` and search for `Device Maintenance Monitor`.
3. Follow the configuration flow to set up the integration:
    - Select the device you want to monitor.
    - Choose the type of monitor: "Runtime", "Power On Count", or "Fixed Interval".
    - Depending on the monitor type, provide additional information such as:
      - Interval: The duration for the "Runtime" or "Fixed Interval" monitor types.
      - Count: The count for the "Power On Count" monitor type.

## Usage

### Resetting the Maintenance Data

After performing maintenance on the device, press the `button.reset_maintenance` to reset the maintenance data and start a new tracking period.

### Example Automation

You can create automations based on the entities provided by this integration. For example, send a notification when the device needs maintenance:

```yaml
automation:
  - alias: Notify Maintenance Needed
    trigger:
      [...]
    action:
      [...]
```

## Contributions
Contributions are welcome! If you have any ideas, feel free to open an issue or submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
Special thanks to the Home Assistant community for their support and contributions.

---

For any issues or feature requests, please open an issue on the GitHub repository.

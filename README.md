# Device Maintenance Monitor

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/docs/faq/custom_repositories)

A custom Home Assistant integration to monitor the maintenance of any device. It supports three types of maintenance monitors: Runtime, Power On Count, and Fixed Interval.

## Why It Needed?
Maintaining the various devices in our homes can be challenging, especially when their usage varies greatly. 
Standard maintenance schedules often don't account for actual usage, leading to either overdue maintenance or unnecessary servicing. 
This is particularly problematic for devices with variable usage patterns, like air conditioners or water heaters. 
The Device Maintenance Monitor custom component for Home Assistant addresses this issue by providing a tailored maintenance reminder system based on actual device usage rather than just fixed intervals. 
This ensures that each device gets the attention it needs based on how much it is actually used.

### Features

- Track the last maintenance date.
- Monitor total runtime hours, power on count, or fixed interval depending on the type of monitor.
- Calculate remaining hours or counts until the device needs maintenance.
- Provide a boolean sensor indicating if the device needs maintenance.
- Include a button to reset the maintenance data.

### Use Cases

- **Air Conditioners:** Different usage patterns in different rooms can result in varied maintenance needs. This integration helps track actual usage to provide accurate reminders.
- **Water Filters:** Monitor the amount of water passed through the filter to ensure regular maintenance and prevent unexpected breakdowns.
- **Washing Machines:** Track the number of times a device is used to clean filters after a set number of uses.


## Installation

### Manual Installation

1. Download the `device_maintenance_monitor` directory from the [latest release](https://github.com/rafael-zilberman/device-maintenance-monitor-custom-component/releases/latest).
2. Copy the `device_maintenance_monitor` directory to your `custom_components` directory in your Home Assistant configuration directory.

### HACS Installation

1. Open Home Assistant and go to HACS.
2. Click on "Integrations" and then the three dots in the top right corner.
3. Select "Custom repositories".
4. Add the repository URL: `https://github.com/rafael-zilberman/device-maintenance-monitor-custom-component` and select the category as "Integration".
5. Find "Device Maintenance Monitor" in the HACS store and install it.
6. [Click here to add Device Maintenance Monitor to your Home Assistant](https://my.home-assistant.io/redirect/config_flow_start/?domain=device_maintenance_monitor)

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

You can create automations based on the entities provided by this integration. For example, send a notification when the device needs maintenance using the Home Assistant "alert" integration:

```yaml
alert:
  ac_maintenance_needed:
    name: "AC Maintenance Needed"
    done_message: "AC Maintenance has been performed"
    entity_id: binary_sensor.ac_maintenance_needed
    state: "on"
    repeat: 60
    can_acknowledge: true
    skip_first: false
    notifiers:
      - mobile_app_your_device
```

## Contributions
Contributions are welcome! If you have any ideas, feel free to open an issue or submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
Special thanks to the Home Assistant community for their support and contributions.

---

For any issues or feature requests, please open an issue on the GitHub repository.

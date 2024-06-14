# HVAC Filter Monitor

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/docs/faq/custom_repositories)

A custom Home Assistant integration to monitor the HVAC filter usage and calculate the replacement date based on the hours the HVAC system has been running.

## Features

- Track the last filter replacement date.
- Monitor total filter running hours.
- Calculate remaining hours until the filter needs to be changed.
- Compute average usage hours per day.
- Provide a boolean sensor indicating if the filter needs to be cleaned or replaced.
- Include a button to reset the filter usage.

## Installation

### Manual Installation

1. Download the `hvac_filter` directory from the [latest release](https://github.com/your_github_username/hvac_filter/releases/latest).
2. Copy the `hvac_filter` directory to your `custom_components` directory in your Home Assistant configuration directory.

### HACS Installation

1. Open Home Assistant and go to HACS.
2. Click on "Integrations" and then the three dots in the top right corner.
3. Select "Custom repositories".
4. Add the repository URL: `https://github.com/your_github_username/hvac_filter` and select the category as "Integration".
5. Find "HVAC Filter Monitor" in the HACS store and install it.

## Configuration

1. After installation, go to Home Assistant and navigate to `Configuration` -> `Integrations`.
2. Click on `Add Integration` and search for `HVAC Filter Monitor`.
3. Follow the configuration flow to set up the integration:
    - Select the HVAC device you want to monitor.
    - Input the runtime hours after which you want to replace the filter.

## Entities Created

- `sensor.last_filter_replacement_date`: The date when the filter was last replaced.
- `sensor.total_filter_running_hours`: Total hours the HVAC system has been running since the last filter replacement.
- `sensor.remaining_hours_until_filter_change`: Remaining hours until the filter needs to be changed.
- `sensor.average_usage_hours_per_day`: Average daily usage hours of the HVAC system.
- `binary_sensor.filter_needs_replacement`: Indicates if the filter needs to be cleaned or replaced.
- `button.reset_filter`: Button to reset the filter usage data.

## Usage

### Resetting the Filter

After replacing or cleaning the filter, press the `button.reset_filter` to reset the filter usage data and start a new tracking period.

### Example Automation

You can create automations based on the entities provided by this integration. For example, send a notification when the filter needs to be replaced:

```yaml
automation:
  - alias: Notify Filter Replacement
    trigger:
      platform: state
      entity_id: binary_sensor.filter_needs_replacement
      to: 'on'
    action:
      service: notify.notify
      data:
        message: "The HVAC filter needs to be replaced."
```

## Contributions
Contributions are welcome! If you have any ideas, feel free to open an issue or submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
Special thanks to the Home Assistant community for their support and contributions.

---

For any issues or feature requests, please open an issue on the GitHub repository.

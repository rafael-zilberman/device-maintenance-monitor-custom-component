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

### Entities

The Device Maintenance Monitor integration provides the following entities:

- **Sensor Entities:**
  - `sensor.<device_name>_predicted_maintenance_date`: Displays the predicted date for the next maintenance based on the device's usage.

- **Button Entities:**
  - `button.reset_maintenance`: Resets the maintenance data for the device.

- **Binary Sensor Entities:**
  - `binary_sensor.<device_name>_maintenance_needed`: Indicates whether the device needs maintenance based on the configured criteria.

Replace `<device_name>` with the actual name of your device as configured in Home Assistant.

### Resetting the Maintenance Data

After performing maintenance on the device, press the `button.reset_maintenance` to reset the maintenance data and start a new tracking period.

Another option is to reset the maintenance data is using a service call. You can call the `device_maintenance_monitor.reset_maintenance` service with the following data:

```yaml
service: device_maintenance_monitor.reset_maintenance
data: {}
target:
  entity_id: binary_sensor.my_device_maintenance_needed
```

### Updating the maintenance info manually

You can update the maintenance data manually by calling the `device_maintenance_monitor.update_maintenance_info` service with the following data:

```yaml
service: device_maintenance_monitor.update_maintenance_info
data:
  last_maintenance_date: 2022-01-01
target:
    entity_id: binary_sensor.my_device_maintenance_needed
```

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

### Dashboard

You can create a dashboard to monitor the maintenance status of your devices. Here is an example of a Lovelace card to display the maintenance status of a devices using the `auto-entities` card:

```yaml
type: custom:auto-entities
filter:
  include:
    - integration: device_maintenance_monitor
      domain: binary_sensor
      options:
        type: tile
  exclude: []
sort:
  method: attribute
  attribute: predicted_maintenance_date
card:
  type: vertical-stack
  title: 'Devices'
card_param: cards
```

You can also use the custom card `device-maintenance-monitor-card` to display the maintenance status of your devices. You can find the card template [here](lovelace/card_device_maintenance.yaml).

```yaml
type: custom:auto-entities
filter:
  include:
    - integration: device_maintenance_monitor
      domain: binary_sensor
      options:
        type: 'custom:button-card'
        template: card_device_maintenance
        variables:
          ulm_card_card_device_maintenance_force_background_color: true
  exclude: []
sort:
  method: attribute
  attribute: predicted_maintenance_date
card:
  type: vertical-stack
  title: 'Devices'
card_param: cards
```

## Contributions
Contributions are welcome! If you have any ideas, feel free to open an issue or submit a pull request.

### Development

To set up a development environment, clone the repository and install the dependencies:
    
 ```bash
git clone git@github.com:rafael-zilberman/device-maintenance-monitor-custom-component.git
cd device_maintenance_monitor_custom_component
pip install -r requirements.txt
 ```

You can use Docker Compose to set up a Home Assistant development environment with the custom component.   
First, ensure Docker and Docker Compose are installed on your machine.  
Use the provided compose.yaml file to start the Home Assistant container with the custom component:  
```bash
docker-compose -f compose.yaml up
```
Home Assistant instance with the component installed will be accessible at http://localhost:8123. You can now develop and test the custom component within this environment.
The custom component files are mounted to the Home Assistant container, so any changes you make to the files will be reflected in the Home Assistant instance after a restart.

## Pull Requests
If you submit a pull request, please follow these guidelines:

1. **Fork the repository** and create your branch from `dev`.
2. **Create a new branch** following the naming convention: `feature/<Feature requests issue id>-your-feature-name` or `bugfix/<Bug report issue id>-your-fix-name`.
3. **Update documentation** to reflect any changes or additions (including README.md if necessary).
4. **Ensure your code adheres to the project's coding standards**.
   1. Run `black .` to format your code and make sure it passes the linting checks.
   2. Make sure to add docstrings to your functions and classes.
5. **Provide a clear description** of the changes and the problem they solve.
6. **Reference any relevant issues** in your pull request description.
7. **Be prepared to make revisions** based on feedback from maintainers.
   1. Address PR agent AI comments before requesting a review from maintainers.
8. **Squash your commits before merging**.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
Special thanks to the Home Assistant community for their support and contributions.

---

For any issues or feature requests, please open an issue on the GitHub repository.

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/baadrdeen/Meraki_vpn_hub_updater)
[![Run in Cisco Cloud IDE](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-runable-icon.svg)](https://developer.cisco.com/devenv/?id=devenv-vscode-base&GITHUB_SOURCE_REPO=https://github.com/baadrdeen/Meraki_vpn_hub_updater)

# Meraki AutoVPN Hub Update Script

The Meraki AutoVPN Hub Update Script is a Python script that allows you to update AutoVPN settings for Meraki networks using the Meraki API. It provides a convenient way to modify the hub and hub order configuration for multiple networks at once.

## Features

- Updates AutoVPN hub and hub order for Meraki networks
- Supports simulation mode to test updates without making actual changes
- Provides the ability to restore VPN settings from a backup file
- Generates a report with details of the VPN settings updates

## Prerequisites

Before using the script, ensure you have the following:

- Python 3.7 or later installed
- Meraki Dashboard API key
- Meraki organization with networks to update

## Installation

1. Clone this repository to your local machine:

```bash
git clone https://github.com/your-username/meraki-autovpn-hub-update.git
```

2. Navigate to the project directory:

```bash
cd meraki-autovpn-hub-update
```

3. Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `config.yaml` file in the project directory.

2. Open the `config.yaml` file and provide the following information:

```yaml
org_id: YOUR_ORG_ID
target: all
hub_order: secondary
old_hub_name: Old Hub Name
new_hub_name: New Hub Name
```

- Replace `YOUR_ORG_ID` with your actual Meraki organization ID.
- Adjust the `target`, `hub_order`, `old_hub_name`, and `new_hub_name` parameters as needed.

## Usage

The script can be executed using the command-line interface. There are two modes available: simulation mode and deploy mode.

To run the script in **simulation mode**:

```bash
python meraki_autovpn_hub_update.py -s
```

- The `-s` or `--simulate` flag enables simulation mode.
- In this mode, the script will simulate the API requests and indicate them in the logs file.
- No actual changes will be made to your Meraki networks.

To run the script in **deploy mode**:

```bash
python meraki_autovpn_hub_update.py -d
```

- The `-d` or `--deploy` flag activates deploy mode.
- In this mode, the script will make changes to your Meraki networks based on the specified configuration.
- **Caution:** Verify your configuration before running in deploy mode to ensure the desired changes are applied.

**Note:** By default, the script runs in simulation mode if no mode is specified.

## Workflow

The script follows the following logical workflow:

1. **Introduction**: Upon execution, the script displays an introduction and provides information about the location of logs, backup files, and the report file.

2. **Restore Mode (Optional)**: If the `-r` or `--restore` flag is provided, the script restores VPN settings from a backup file.

3. **Update Mode**: If not in restore mode, the script loads the configuration from the `config.yaml` file and validates it.

4. **Simulation Mode (Default)**: If in simulation mode, the script performs a simulation of the VPN settings updates and logs the simulated API requests.

5. **Deploy Mode**: If in deploy mode, the script makes changes to the specified Meraki networks based on the configuration.

6. **Backup**: Before making any changes, the script creates a backup of the current VPN settings for each network.

7. **Update VPN Hubs**: The script updates the VPN hubs and hub order for the specified networks.

8. **Result Report**: Upon completion, the script generates a report with details of the VPN settings updates and saves it as an Excel file.

## Logs, Backup Files, and Report

- **Logs**: The logs for the script execution are stored in the `Logs` directory.
- **Backup Files**: VPN settings backup files are stored in the `Backup` directory.
- **Report**: The result of VPN settings updates is saved as an Excel file in the `Report` directory.


## Acknowledgements

This script was developed using the Meraki Dashboard API and the [rich](https://rich.readthedocs.io) library.

## Disclaimer

- This script comes with no warranty or support. Use it at your own risk.
- Double-check your configuration and backup your VPN settings before running the script in deploy mode.
- Review the script and understand the implications before making changes to your Meraki networks.

## Author

[Badr-eddine](https://www.linkedin.com/in/badreddine-aharchi)

## Contributing

Contributions are welcome! If you encounter any issues or have suggestions for improvements, please create an issue or submit a pull request.


## License

This project is licensed under the [MIT License](LICENSE).

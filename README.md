# Meraki VPN Settings Update Script

This script allows you to update the VPN settings for all networks in a Meraki organization. It leverages the Meraki Dashboard API to retrieve and update the VPN configuration.

## Prerequisites

- Python 3.x
- Meraki Dashboard API key ([Meraki Dashboard API Documentation](https://developer.cisco.com/meraki/api/))
- Required Python libraries:
  - `meraki`
  - `pandas`
  - `pyyaml`
  - `openpyxl`

## Installation

1. Clone the repository:

```shell
git clone https://github.com/your-username/meraki-vpn-settings-update.git
```

2. Install the required dependencies:

```shell
pip install -r requirements.txt
```

## Configuration

1.  Make sure to include all the necessary libraries in the "Prerequisites" section, and also update the "Installation" section to mention the installation of required dependencies using `pip install -r requirements.txt`.
2.  Open the `config.yaml` file and provide the following information:
   - `org_id`: Your Meraki organization ID.
   - `old_hub_name`: The name of the old VPN hub you want to replace.
   - `new_hub_name`: The name of the new VPN hub you want to set.
3. Save the `config.yaml` file.

## Usage

To update the VPN settings, run the script with the following command:

```shell
python MerakiVPN-HubUpdater.py -s  # For simulate mode (default)
```

```shell
python MerakiVPN-HubUpdater.py -d  # For deploy mode
```

- Simulate Mode (`-s` or `--simulate`): This mode simulates the VPN settings update without actually applying the changes. It is useful for testing and verifying the configuration before deployment.
- Deploy Mode (`-d` or `--deploy`): This mode applies the VPN settings changes to the networks.

After execution, the script will generate an Excel file named `vpn_settings_update.xlsx` containing the network ID, network name, old hub ID, new hub ID, old VPN settings configuration, and new VPN settings configuration for each updated network.

## Contributing

Contributions are welcome! If you encounter any issues or have suggestions for improvements, please create an issue or submit a pull request.

## Author

[Badr-eddine](https://www.linkedin.com/in/badreddine-aharchi)

## License

This project is licensed under the [MIT License](LICENSE).

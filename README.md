# Meraki VPN Settings Update Script

Managing VPN settings across multiple networks can be a time-consuming task. This script aims to automate and streamline the process by providing a simple and efficient way to update VPN hub configurations. Whether you need to replace an existing VPN hub with a new one or make changes to the VPN configuration, this script allows you to perform these updates across multiple networks in a consistent and scalable manner.

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
git clone https://github.com/baadrdeen/Meraki_vpn_hub_updater.git
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
python3 MerakiVPN-HubUpdater.py -s  # For simulate mode (default)
```

```shell
python3 MerakiVPN-HubUpdater.py -d  # For deploy mode
```

- Simulate Mode (`-s` or `--simulate`): This mode simulates the VPN settings update without actually applying the changes. It is useful for testing and verifying the configuration before deployment.
- Deploy Mode (`-d` or `--deploy`): This mode applies the VPN settings changes to the networks.

The script follows the following workflow:

1. Read the configuration from `config.yaml`, including the organization ID, old hub name, and new hub name.
2. Authenticate with the Meraki Dashboard API using the provided API key.
3. Retrieve the list of networks in the organization.
4. Find the network IDs for the old and new VPN hubs based on their names.
5. Create an empty DataFrame to store the result of the VPN settings update.
6. For each network:
   - Retrieve the current VPN settings.
   - If both old and new hub IDs are found:
     - Update the VPN hub ID with the new value.
     - Apply the updated VPN settings to the network.
     - Append the network ID, network name, old hub ID, new hub ID, old VPN settings configuration, and new VPN settings configuration to the result DataFrame.
   - If either the old or new hub ID is not found, skip the network.
   - Introduce a delay between API calls to comply with rate limits.
7. Save the result DataFrame to an Excel file named `vpn_settings_update.xlsx`.
8. Print a success message and the path to the generated Excel file.

## Contributing

Contributions are welcome! If you encounter any issues or have suggestions for improvements, please create an issue or submit a pull request.

## Author

[Badr-eddine](https://www.linkedin.com/in/badreddine-aharchi)

## License

This project is licensed under the [MIT License](LICENSE).

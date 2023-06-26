# Meraki VPN Hub Updater

The Meraki VPN Hub Updater is a Python script that allows you to update the VPN hub ID for multiple Meraki networks simultaneously. It uses the Meraki Dashboard API to fetch the current VPN settings for each network and update the hub ID with a new value.

## Prerequisites

Before using the Meraki VPN Hub Updater, ensure that you have the following:

- **Python 3.6 or higher**: The script requires Python to be installed on your machine. You can download Python from the official website: [https://www.python.org/downloads](https://www.python.org/downloads).

- **Meraki Dashboard API key**: In order to authenticate and access your Meraki organization, you'll need an API key. Follow these steps to obtain the API key:

  1. Log in to the Meraki Dashboard.
  2. Go to **Organization > Settings**.
  3. Under the **Dashboard API access** section, click on the **Enable API** button.
  4. Click on **Generate new API key** to obtain a new API key.
  5. Copy the generated API key and store it securely.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/meraki-vpn-hub-updater.git
   ```

2. Navigate to the project directory:

   ```bash
   cd meraki-vpn-hub-updater
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Open the `config.py` file.

2. Replace the placeholder values with your actual Meraki organization ID, old hub name, and new hub name.

   ```python
   ORG_ID = 'YOUR_ORG_ID'
   OLD_HUB_NAME = 'OLD_HUB_NAME'
   NEW_HUB_NAME = 'NEW_HUB_NAME'
   ```

## Usage

Run the script by executing the following command:

```bash
python main.py
```

The script will fetch the list of networks in your organization, find the network IDs based on the provided hub names, and update the VPN hub ID for each network. The script will output the progress and any errors encountered during the update process. Once the updates are complete, a file named `vpn_settings_update.xlsx` will be generated, containing the network IDs, network names, old hub IDs, new hub IDs, old VPN settings configuration, and new VPN settings configuration.

## Contributing

Contributions to this script are welcome. If you encounter any issues or have suggestions for improvements, please submit a pull request or open an issue on GitHub.

## Author

[Badr-eddine](https://www.linkedin.com/in/badreddine-aharchi)

## License

This project is licensed under the [MIT License](LICENSE).

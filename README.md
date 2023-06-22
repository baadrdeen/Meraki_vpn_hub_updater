# Meraki VPN Hub Updater

This Python script allows you to update the VPN hub ID for multiple Meraki networks in one go using the Meraki library. It retrieves the VPN settings for each network and updates the hub ID based on the provided hub name.

## Prerequisites

Before running the script, ensure you have the following:

- Python 3.x installed on your machine.
- Meraki library installed. You can install it using `pip install meraki`.
- Meraki API key exported as an environment variable with the name `MERAKI_DASHBOARD_API_KEY`. You can obtain an API key from the Meraki Dashboard.

## Usage

1. Clone the repository or download the script file to your local machine.

2. Open the script file `vpn_hub_updater.py` in a text editor.

3. Modify the following variables at the top of the script:

   - `org_id`: Replace `'YOUR ORG ID'` with your actual organization ID.
   - `hub_name`: Replace `'YOUR HUB NAME'` with the desired VPN hub name.

4. By default, the script is set to simulate the operation (`simulate=True`). It will only plan the updates without actually making changes to the Meraki networks. If you want to deploy the changes in the production environment, set `simulate=False` in the `dashboard` initialization.

5. Save the changes.

6. Open a terminal or command prompt and navigate to the directory where the script is located.

7. Run the script using the command `python vpn_hub_updater.py`.

   The script will retrieve the networks in your organization, find the hub ID based on the provided hub name, and update the VPN hub ID for each network. The progress and results will be displayed in the terminal.

   Note: The script automatically introduces a delay between API calls to comply with the Meraki API rate limit of 10 calls per second.

8. Monitor the output in the terminal for any errors or successful updates.

## License

This project is licensed under the [MIT License](LICENSE).

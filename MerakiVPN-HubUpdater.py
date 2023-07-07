#!/usr/bin/env python3
__author__ = "AHARCHI_Badr-eddine"

import os
import meraki
import concurrent.futures
import time
import pandas as pd
import yaml
import argparse
import json
from tqdm import tqdm
from rich import print
from rich.console import Console
import sys

# Delay between API calls to comply with the rate limit (0.1 seconds (100 milliseconds))
API_CALL_DELAY = 0.1

def find_hub_id_by_name(networks, hub_name):
    """
    Finds the hub ID based on the hub name in the given list of networks.

    Arguments:
    - networks: List of network dictionaries
    - hub_name: Name of the hub to search for

    Returns:
    - Hub ID if found, None otherwise
    """
    for network in networks:
        if network['name'] == hub_name:
            return network['id']
    return None

def backup_vpn_settings(network_id, vpn_settings):
    """
    Backs up the VPN settings for a given network ID.

    Arguments:
    - network_id: Network ID
    - vpn_settings: VPN settings dictionary
    """    
    try:
        if not os.path.exists("Backup"):
            os.makedirs("Backup")
        # Load existing backup file if it exists
        backup_data = []
        if os.path.exists('Backup/vpn_settings_backup.json'):
            with open('Backup/vpn_settings_backup.json', 'r') as file:
                backup_data = json.load(file)

        # Append the current VPN settings to the backup data
        backup_data.append({network_id: vpn_settings})

        # Save the updated backup data to the backup file
        with open('Backup/vpn_settings_backup.json', 'w') as file:
            json.dump(backup_data, file, indent=4)

        dashboard._logger.info(f'Successfully backed up VPN settings for network ID: {network_id}')

    except Exception as e:
        dashboard._logger.error(f'Error backing up VPN settings for network ID: {network_id}. Error message: {e}')
        print(f'[red]|---> [!]  Error backing up VPN settings for network ID: {network_id}. Error message: {e}')

def restore_config():
    """
    Restores the VPN settings from the backup file.
    """
    try:
        # Check if backup file exists
        if os.path.exists('Backup/vpn_settings_backup.json'):
            with open('Backup/vpn_settings_backup.json', 'r') as file:
                backup_data = json.load(file)

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                for entry in tqdm(backup_data, desc='Restoring networks',colour='#00ff00', total=len(backup_data)):
                    network_id, vpn_settings = list(entry.items())[0]  # Convert dict_items to list and access the first item
                    futures.append(executor.submit(restore_vpn_settings, network_id, vpn_settings))
                    time.sleep(API_CALL_DELAY)

                concurrent.futures.wait(futures)

            dashboard._logger.info('Meraki AutoVPN settings restore completed!')
            print()
            print(f'[green]|---> [ \N{check mark} ] Meraki AutoVPN settings restore completed!')
            print()

        else:
            dashboard._logger.error('No VPN settings backup file found.')
            print(f'[red]|---> [!] No VPN settings backup file found.')

    except Exception as e:
        dashboard._logger.error(f'Error restoring VPN settings. Error message: {e}')
        print(f'[red]|---> [!]  Error restoring VPN settings. Error message: {e}')

def restore_vpn_settings(network_id, vpn_settings):
    """
    Restores the VPN settings for a given network ID.

    Arguments:
    - network_id: Network ID
    - vpn_settings: VPN settings dictionary

    """
    try:
        response = dashboard.appliance.updateNetworkApplianceVpnSiteToSiteVpn(
            network_id, vpn_settings['mode'], hubs=vpn_settings['hubs'], subnets=vpn_settings['subnets']
        )

        dashboard._logger.info(f'Successfully restored VPN settings for network ID: {network_id}')

    except meraki.APIError as e:
        dashboard._logger.error(f'Error restoring VPN settings for network ID: {network_id}. Error message: {e}')
        print(f'[red]|---> [!]  Error restoring VPN settings for network ID: {network_id}. Error message: {e}')

def update_vpn_hub(network_id, old_hub_id, new_hub_id, hub_order, result_df):
    """
    Updates the VPN hub and hub order for a given network ID.

    Arguments:
    - network_id: Network ID
    - old_hub_id: Old hub ID
    - new_hub_id: New hub ID
    - hub_order: Hub order option (primary, secondary, or switch)
    - result_df: Result DataFrame to store network information
    """
    try:
        # Get the current VPN settings for the network
        vpn_settings = dashboard.appliance.getNetworkApplianceVpnSiteToSiteVpn(network_id)
        backup_vpn_settings(network_id, vpn_settings)

        if hub_order == 'primary' or hub_order == 'secondary':
            updated_hubs = []
            primary_hub = None

            # Iterate over the existing hubs and find the new hub
            for hub in vpn_settings['hubs']:
                if hub['hubId'] == new_hub_id:
                    primary_hub = {'hubId': new_hub_id, 'useDefaultRoute': hub['useDefaultRoute']}
                else:
                    updated_hubs.append(hub)

            # Insert the new hub at the beginning or end of the updated hubs list based on the hub order option
            if hub_order == 'primary' and primary_hub:
                updated_hubs.insert(0, primary_hub)
            elif hub_order == 'secondary' and primary_hub:
                updated_hubs.append(primary_hub)

        elif hub_order == 'switch':
            # Switch the order of the existing hubs
            updated_hubs = vpn_settings['hubs'][::-1]

        else:
            dashboard._logger.error(f'Invalid hub order option: {hub_order}')
            print(f'[red]|---> [!] Invalid hub order option: {hub_order}')
            return

        # Update the VPN settings with the new hub and hub order
        response = dashboard.appliance.updateNetworkApplianceVpnSiteToSiteVpn(
             network_id, vpn_settings['mode'], hubs=updated_hubs, subnets=vpn_settings['subnets']
        )

        dashboard._logger.info(f'Successfully updated VPN hub and hub order for network ID: {network_id}')


        # Get the network name
        network_name = dashboard.networks.getNetwork(network_id)['name']

        # Append old and new settings to the result DataFrame
        old_settings_config = str(vpn_settings)
        new_settings_config = str(response)
        result_df.loc[len(result_df)] = [network_id, network_name, old_hub_id, new_hub_id, old_settings_config, new_settings_config]

    except meraki.APIError as e:
        dashboard._logger.error(f'Error updating VPN hub and hub order for network ID: {network_id}. Error message: {e}')
        print(f'[red]|---> [!]  Error updating VPN hub and hub order for network ID: {network_id}. Error message: {e}')

def update_all_vpn_hubs(org_id, target, old_hub_name, new_hub_name, hub_order):
    """
    Updates the VPN hubs and hub order for all networks in an organization.

    Arguments:
    - org_id: Organization ID
    - target: Target networks (all or list of network IDs)
    - old_hub_name: Name of the old hub
    - new_hub_name: Name of the new hub
    - hub_order: Hub order option (primary, secondary, or switch)

    Returns:
    - Result DataFrame with network information
    """
    try:
        # Get a list of networks in the organization
        networks = dashboard.organizations.getOrganizationNetworks(org_id)

        # Find the old and new hub IDs by name
        if hub_order != "switch":
            old_hub_id = find_hub_id_by_name(networks, old_hub_name)
            new_hub_id = find_hub_id_by_name(networks, new_hub_name)
        elif hub_order == "switch":
            old_hub_id = None
            new_hub_id = None

        if (old_hub_id and new_hub_id) or (hub_order == "switch"):
            result_df = pd.DataFrame(
                columns=[
                    "Network ID",
                    "Network Name",
                    "Old Hub ID",
                    "New Hub ID",
                    "Old VPN Settings Config",
                    "New VPN Settings Config",
                ]
            )

            # Check if the target is set to "all"
            if target == "all":
                target_network_ids = [network["id"] for network in networks]
            else:
                # Assume target contains specific network IDs
                target_network_ids = target

            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Iterate over each network and submit update tasks for the target networks only
                futures = []
                for network in tqdm(
                    networks,
                    desc="Updating networks",
                    colour="#00ff00",
                    total=len(networks),
                ):
                    network_id = network["id"]
                    if network_id in target_network_ids:
                        vpn_settings = dashboard.appliance.getNetworkApplianceVpnSiteToSiteVpn(network_id)

                        # Skip updating network if mode is "hub"
                        if vpn_settings["mode"] == "hub":
                            dashboard._logger.info(
                                f'Skipping network ID: {network_id} - VPN mode is "hub"'
                            )
                            continue

                        futures.append(
                            executor.submit(
                                update_vpn_hub,
                                network_id,
                                old_hub_id,
                                new_hub_id,
                                hub_order,
                                result_df,
                            )
                        )
                        time.sleep(API_CALL_DELAY)  # Introduce a delay between API calls

                # Wait for all tasks to complete
                concurrent.futures.wait(futures)
            print()
            print(f'[green]|---> [ \N{check mark} ] Meraki AutoVPN settings update completed!')
            print()
            return result_df

        else:
            dashboard._logger.error(
                f'Error: VPN hub name "{old_hub_name}" or "{new_hub_name}" not found.'
            )
            print(
                f'[red]|---> [!] Error: VPN hub name "{old_hub_name}" or "{new_hub_name}" not found.'
            )
            return None

    except meraki.APIError as e:
        dashboard._logger.error(f'Error fetching networks. Error message: {e}')
        print(f'[red]|---> [!]  Error fetching networks. Error message: {e}')



def load_yaml_config(config_file):
    """
    Loads the YAML configuration file.

    Arguments:
    - config_file: Path to the YAML configuration file

    Returns:
    - Configuration dictionary
    """
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def delete_backup_if_exists(file_path):
    """
    Delete file if exists.
    """
    if os.path.exists(file_path):
        os.remove(file_path)

def validate_config(config):
    """
    Validates the configuration dictionary.

    Arguments:
    - config: Configuration dictionary

    ReturnsContinued:

    - Hub order option (primary, secondary, or switch) if valid, False otherwise
    """
    required_fields = ['org_id', 'target']
    if 'hub_order' in config:
        hub_order = config['hub_order']
        if hub_order not in ['primary', 'secondary', 'switch']:
            return False
        if hub_order == 'primary' or hub_order == 'secondary':
            required_fields.extend(['old_hub_name', 'new_hub_name'])
    else:
        hub_order = 'secondary'

    for field in required_fields:
        if field not in config or config[field] is None:
            return False

    return hub_order

def main(simulate, restore):
    """
    Main function to execute the script.

    Arguments:
    - simulate: Boolean flag to simulate the update without making changes
    - restore: Boolean flag to restore VPN settings from backup
    """

    console = Console()

    # Define the location of logs, backup files, and generated files
    LOG_DIR = "Logs"
    BACKUP_DIR = "Backup"
    REPORT_DIR = "Report"
    CONFIG_FILE = "config.yaml"

    # Print introduction
    console.print()
    console.print("[bold italic]This script allows you to update AutoVPN settings for Meraki networks.")
    console.print("[bold italic]It retrieves the necessary configuration from a YAML file and uses the Meraki API for the updates.")
    console.print("[bold italic]If you encounter any issues, please check the logs for further information", style="yellow")
    console.print()
    console.print("[bold italic] Logs, backup files, and the report file will be stored in the following locations:")
    console.print(f"[cyan]- Config File: {os.path.abspath(CONFIG_FILE)}[/cyan]")
    console.print(f"[cyan]- Logs: {os.path.abspath(LOG_DIR)}[/cyan]")
    console.print(f"[cyan]- Backup Files: {os.path.abspath(BACKUP_DIR)}[/cyan]")
    console.print(f"[cyan]- Report File: {os.path.abspath(REPORT_DIR)}[/cyan]")
    console.print()
    if restore:
        # Restore VPN settings from backup
        print(f'[bold green]|---> [+] Starting AutoVPN settings restore...')
        if simulate:
            console.print("[yellow]|---> [*] Simulation Mode: Simulated API requests will be indicated in the logs file.")
            console.print()
        else:
            console.print("[yellow]|---> [*] Deploy Mode: This operation will make changes to your Meraki networks.")
            console.print()
            console.print("[orange_red1]|--> [?] Proceed with caution! Enter [Y/y] to confirm and continue: ")
            confirm = input()
            if confirm.lower() != "y":
                console.print("[red]|---> [!] Operation aborted by user!")
                sys.exit()

        restore_config()
    else:
        # Load config from YAML file
        config = load_yaml_config('config.yaml')

        # Validate config and retrieve hub_order
        hub_order = validate_config(config)
        if hub_order is False:
            dashboard._logger.error('Error: Invalid config file.')
            print(f'[red]|---> [!] Error: Invalid config file.')
            return

        org_id = config['org_id']
        target = config['target']
        if hub_order!='switch':
            old_hub_name = config['old_hub_name']
            new_hub_name = config['new_hub_name']
        elif hub_order=='switch':
            old_hub_name = ""
            new_hub_name = ""
        
        print(f'[bold green]|---> [+] Starting AutoVPN settings update...')
        if simulate:
            console.print("[yellow]|---> [*] Simulation Mode: Simulated API requests will be indicated in the logs file.")
            console.print()
        else:
            console.print("[yellow]|---> [*] Deploy Mode: This operation will make changes to your Meraki networks.")
            console.print()
            console.print("[orange_red1]|--> [?] Proceed with caution! Enter [Y/y] to confirm and continue: ")
            confirm = input()
            if confirm.lower() != "y":
                console.print("[red]|--> [?] Operation aborted by user!")
                sys.exit()

        delete_backup_if_exists('Backup/vpn_settings_backup.json')    
        result_df = update_all_vpn_hubs(org_id,target ,old_hub_name, new_hub_name, hub_order)

        if not os.path.exists("Report"):
            os.makedirs("Report")

        if result_df is not None and hub_order!="switch":
            # Save the report DataFrame to a Excel file
            result_df.to_excel('Report/vpn_settings_update_result.xlsx', index=False)
            dashboard._logger.warning('VPN settings update completed. Result saved to vpn_settings_update_result.xlsx')

# Parse command line arguments
parser = argparse.ArgumentParser(description='Meraki VPN Hub Update Script')
parser.add_argument('-s', '--simulate', action='store_true', help='Simulate mode (default)')
parser.add_argument('-d', '--deploy', action='store_true', help='Deploy mode')
parser.add_argument('-r','--restore', action='store_true', help='Restore VPN settings from backup')
args = parser.parse_args()

# Determine simulate or deploy mode based on command line arguments
simulate = True  # Default is simulate mode
if args.deploy:
    simulate = False

if not os.path.exists("Logs"):
    os.makedirs("Logs")
# Create a Meraki Dashboard API session (API key retrieved from environment variable MERAKI_DASHBOARD_API_KEY )
dashboard = meraki.DashboardAPI(output_log=True, print_console=False,simulate=simulate,log_path='Logs/',log_file_prefix='meraki_hub_updater_')

# Execute the script with command line arguments
main(simulate, args.restore)


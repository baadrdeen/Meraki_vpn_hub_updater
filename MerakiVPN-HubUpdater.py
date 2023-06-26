#!/usr/bin/env python3
__author__ = "AHARCHI_Badr-eddine"

import os
import meraki
import concurrent.futures
import time
import pandas as pd
import yaml
import argparse

# Create a Meraki API session with API key retrieved from environment variable
API_KEY = os.environ.get('MERAKI_DASHBOARD_API_KEY')

# Delay between API calls to comply with the rate limit (0.1 seconds (100 milliseconds))
API_CALL_DELAY = 0.1

def find_hub_id_by_name(networks, hub_name):
    for network in networks:
        if network['name'] == hub_name:
            return network['id']
    return None

def update_vpn_hub(network_id, old_hub_id, new_hub_id, result_df, simulate):
    try:
        # Get the current VPN settings for the network
        vpn_settings = dashboard.appliance.getNetworkApplianceVpnSiteToSiteVpn(network_id)

        if old_hub_id and new_hub_id:
            updated_hubs = []
            for hub in vpn_settings['hubs']:
                if hub['hubId'] == old_hub_id:
                    updated_hubs.append({'hubId': new_hub_id, 'useDefaultRoute': True})
                else:
                    updated_hubs.append(hub)

            # Update the VPN settings
            if simulate:
                response = {'simulate': True}  # Simulate mode
            else:
                response = dashboard.appliance.updateNetworkApplianceVpnSiteToSiteVpn(
                    network_id, vpn_settings['mode'], hubs=updated_hubs, subnets=vpn_settings['subnets']
                )

            print(f'Successfully updated VPN hub ID for network ID: {network_id}')
            print(response)

            # Get the network name
            network_name = dashboard.networks.getNetwork(network_id)['name']

            # Append old and new settings to the result DataFrame
            old_settings_config = str(vpn_settings)
            new_settings_config = str(response)
            result_df.loc[len(result_df)] = [network_id, network_name, old_hub_id, new_hub_id, old_settings_config, new_settings_config]

    except meraki.APIError as e:
        print(f'Error updating VPN hub ID for network ID: {network_id}. Error message: {e}')

def update_all_vpn_hubs(org_id, old_hub_name, new_hub_name, simulate):
    try:
        # Get a list of networks in the organization
        networks = dashboard.organizations.getOrganizationNetworks(org_id)

        # Find the old and new hub IDs by name
        old_hub_id = find_hub_id_by_name(networks, old_hub_name)
        new_hub_id = find_hub_id_by_name(networks, new_hub_name)

        if old_hub_id and new_hub_id:
            result_df = pd.DataFrame(columns=['Network ID', 'Network Name', 'Old Hub ID', 'New Hub ID', 'Old VPN Settings Config', 'New VPN Settings Config'])

            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Iterate over each network and submit update tasks
                futures = []
                for network in networks:
                    futures.append(executor.submit(update_vpn_hub, network['id'], old_hub_id, new_hub_id, result_df, simulate))
                    time.sleep(API_CALL_DELAY)  # Introduce a delay between API calls

                # Wait for all tasks to complete
                concurrent.futures.wait(futures)

            return result_df

        else:
            print(f'Error: VPN hub name "{old_hub_name}" or "{new_hub_name}" not found.')
            return None

    except meraki.APIError as e:
        print(f'Error fetching networks. Error message: {e}')

def load_yaml_config(config_file):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def validate_config(config):
    required_fields = ['org_id', 'old_hub_name', 'new_hub_name']
    for field in required_fields:
        if field not in config:
            return False
    return True

def main(simulate):
    # Specify the YAML configuration file path
    config_file = 'config.yaml'

    # Load the configuration from YAML file
    config = load_yaml_config(config_file)

    # Validate the configuration
    if not validate_config(config):
        print('Error: Invalid configuration file.')
        return

    org_id = config['org_id']
    old_hub_name = config['old_hub_name']
    new_hub_name = config['new_hub_name']

    result_df = update_all_vpn_hubs(org_id, old_hub_name, new_hub_name, simulate)

    if result_df is not None:
        # Save the results to an Excel file
        result_df.to_excel('vpn_settings_update.xlsx', index=False)
        print('VPN settings update completed. Results saved to vpn_settings_update.xlsx')

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Update VPN settings for all networks in an organization.')
    parser.add_argument('-s', '--simulate', action='store_true', help='Simulate mode (default)')
    parser.add_argument('-d', '--deploy', action='store_true', help='Deploy mode')
    args = parser.parse_args()

    # Determine simulate or deploy mode based on command line arguments
    simulate = True  # Default is simulate mode
    if args.deploy:
        simulate = False

    # Create a Meraki API session with API key retrieved from environment variable
    if API_KEY:
        dashboard = meraki.DashboardAPI(API_KEY, simulate=simulate)
        main(simulate)
    else:
        print('Please make sure that the Meraki API key is exported as an environment variable with the name MERAKI_DASHBOARD_API_KEY')

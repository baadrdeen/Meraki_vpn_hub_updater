import os
import meraki
import concurrent.futures
import time

# Create a Meraki API session with API key retrieved from environment variable
API_KEY = os.environ.get('MERAKI_DASHBOARD_API_KEY')

# Simulate : simulate=True
# Deploy   : simulate=False
dashboard = meraki.DashboardAPI(API_KEY, simulate=True)

# Delay between API calls to comply with the rate limit (0.1 seconds (100 milliseconds))
API_CALL_DELAY = 0.1

def update_vpn_hub(network_id, hub_id):
    try:
        # Get the current VPN settings for the network
        vpn_settings = dashboard.appliance.getNetworkApplianceVpnSiteToSiteVpn(network_id)

        if hub_id:
            # Update the VPN hub ID
            vpn_settings['hubs'] = [{'hubId': hub_id, 'useDefaultRoute': True}]

            # Update the VPN settings
            response = dashboard.appliance.updateNetworkApplianceVpnSiteToSiteVpn(
                network_id, vpn_settings['mode'], hubs=vpn_settings['hubs'], subnets=vpn_settings['subnets']
            )

            print(f'Successfully updated VPN hub ID for network ID: {network_id}')
            print(response)
    except meraki.APIError as e:
        print(f'Error updating VPN hub ID for network ID: {network_id}. Error message: {e}')

def update_all_vpn_hubs(org_id, hub_id):
    try:
        # Get a list of networks in the organization
        networks = dashboard.organizations.getOrganizationNetworks(org_id)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Iterate over each network and submit update tasks
            futures = []
            for network in networks:
                futures.append(executor.submit(update_vpn_hub, network['id'], hub_id))
                time.sleep(API_CALL_DELAY)  # Introduce a delay between API calls

            # Wait for all tasks to complete
            concurrent.futures.wait(futures)
    except meraki.APIError as e:
        print(f'Error fetching networks. Error message: {e}')

def main():
    # Specify the organization ID
    org_id = 'YOUR ORG ID'

    # Specify the VPN hub name
    hub_name = 'YOUR HUB NAME'

    try:
        # Get a list of networks in the organization
        networks = dashboard.organizations.getOrganizationNetworks(org_id)

        # Find the hub ID by name
        hub_id = next((network['id'] for network in networks if network['name'] == hub_name), None)

        if hub_id:
            update_all_vpn_hubs(org_id, hub_id)
        else:
            print(f'Error: VPN hub name "{hub_name}" not found.')
    except meraki.APIError as e:
        print(f'Error fetching networks. Error message: {e}')

if __name__ == '__main__':
    # Execute the main function
    main()

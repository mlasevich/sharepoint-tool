#!/usr/bin/env python3
import sys

from sp_tool.sharepoint import SharepointConnector

TENANT = "mycompany"
SITE = "MyTeam"
# Dummy Credentials
CLIENT_ID = "db87c4c8-9a1a-4b53-8aa7-278fa558af34"
SECRET = "6FuTGk52OPCaSJAlvsJ/AhTsjjZlGpwLqKA2BCx873E="

TENANT = "blackhawknetwork"
SITE = "m3test"
CLIENT_ID = 'dc7c34f3-23c9-4730-9c6c-97a91dc7add4'
SECRET = "bZ4QcMJkTOcAn2rlTPDaxEATlQC+9usjbftx5xzm2cc="


def main():
    """ Simple Example"""
    location = sys.argv[1] if len(sys.argv) > 1 else "/"

    # Create Client
    sharepoint = SharepointConnector(
        tenant=TENANT,
        client_id=CLIENT_ID,
        client_secret=SECRET,
        site_name=SITE
    )

    # Test Connection
    if sharepoint.connected:
        # list all folders and files in default directory
        items = sharepoint.list_folder_contents(location)
        print(f"Found {len(items)} items in {location}")
        for item in items:
            print(f"Found: {item}")
    else:
        print("Failed to connect to sharepoint")


if __name__ == "__main__":
    main()

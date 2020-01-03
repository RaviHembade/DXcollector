# -*- encoding: utf-8 -*-

from dexlib import get_api_access_token
from dexlib import get_devices
from dexlib import get_devices_access_token
from dexlib import get_snmp_data
from dexlib import push_device_data
from dexlib import update_device_online_status
from dexlib import push_device_online_status
from dexlib import get_dashboards
from dexlib import push_device_dashboards

import time

from config import ACCOUNTS


if __name__ == '__main__':
    # Variables Declerations
    devices = []
    dashboards = []

    print("------- Starting DX-SNMP-Module -------")
    
    print(" --- Getting Accesstokens ---")
    user_accounts = []
    for email, password in ACCOUNTS:
        user_accounts.append(get_api_access_token(email, password))
    print(" --- Successfully Acquired Access Tokens ---")
    
    print(" --- Getting Devices ---")
    for _, __, access_token in user_accounts:
        devices += get_devices(access_token)
        dashboards += get_dashboards(access_token)
    print(" --- Successfully Acquired List of Devices ---")
    push_device_dashboards(devices, dashboards)

    print(" --- Starting Device Data Access Loop ---")
    while True:
        for device in devices:
            data = []
            status = 1
            try:
                data, status = get_snmp_data(device)

                if(len(data)>0):
                    push_device_data(device, data)
                
                if( status == 0):
                    device['status'] = 0
                elif(status == 1 and len(data)>0):
                    device['status'] = 0
                else:
                    device['status'] += status
            except:
                time.sleep(2)
        
        devices = update_device_online_status(devices)
        push_device_online_status(devices)
        



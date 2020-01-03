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
from dexlib import SNMPThread, runSNMP

import time
import queue

ACCOUNTS = [
    ("ganesh+planetiware@dataexchange.io", "ganesh@dxfidel")
]

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
    q = queue.Queue()
    while True:
        threadList = [SNMPThread(runSNMP, (device, q)) for device in devices]
        for t in threadList:
            t.setDaemon(True)
            t.start()
        for i in threadList:
            i.join()
        
        while q.empty() != True:
            device, data, status = q.get()

            if(len(data) > 0):
                    push_device_data(device, data)

            for d in devices:
                if(d['id']['id'] == device['id']['id']):
                    if(status == 0):
                        d['status'] = 0
                    elif(status == 1 and len(data) > 0):
                        d['status'] = 0
                    else:
                        d['status'] += status
            
        devices = update_device_online_status(devices)
        push_device_online_status(devices)

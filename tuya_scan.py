import json
import os
from datetime import datetime

import tinytuya
from clientlib import RestApiClient
from config import CONFIG
from core.appinfo import AppInfo

def main():
    client=create_client()

    devices_file='devices.json'
    devices_json=[]

    print("Reading devices.json ...")
    if os.path.exists(devices_file):
        f = open('devices.json')
        devices_json=json.loads(f.read())
        f.close()
    else:
        print(f"!!! File not found pse run python -m tinytuya wizard ({devices_file})!!!")

    print("devices.json readed")

    print("scanning devices ...")
    devices=tinytuya.deviceScan()

    print("*************************************")
    print(devices)
    print("*************************************")
    print("Devices scanned!")


    for key in devices:
        device_id=devices[key]['id']

        device_json=get_device(devices_json, device_id)

        dev=client.read_multible("iot_device", {"id": device_id}, json_out=True, none_if_eof=True)
        if dev==None:
            json_data={
                "id": devices[key]['id'],
                "name": "*** new ***",
                "product_id": devices[key]['productKey'],
                "address": devices[key]['ip'],
                "local_key": "*",
                "version": devices[key]['ver'],
                "class_id": "Bulb",
                "vendor_id": "tuya",
                "status_id": "new",
                "last_scan_on": datetime.now(),
                "location_id": AppInfo.get_location_id(),
            }

            if device_json!=None:
                json_data['product_name']=device_json['product_name']
                json_data['local_key']=device_json['key']
                json_data['icon']=device_json['icon']
                json_data['product_id']=device_json['product_id']
                json_data['name']=device_json['name']
                json_data['class_id']=get_class_by_category(client, device_json['category'])
                json_data['category']=device_json['category']

            print(client.create("iot_device",json_data,json_out=True))
        else:
            json_data={
                "product_id": devices[key]['productKey'],
                "address": devices[key]['ip'],
                "version": devices[key]['ver'],
                "last_scan_on": datetime.now(),
                "location_id": AppInfo.get_location_id(),
            }

            if device_json!=None:
                json_data['product_name']=device_json['product_name']
                json_data['local_key']=device_json['key']
                json_data['icon']=device_json['icon']
                json_data['product_id']=device_json['product_id']
                json_data['name']=device_json['name']
                json_data['class_id']=get_class_by_category(client, device_json['category'])
                json_data['category']=device_json['category']

            print(client.update("iot_device",devices[key]['id'], json_data,json_out=True))


    logoff_client(client)

def get_class_by_category(client, category):
    result=None

    dev_class=client.read_multible("iot_device_categorie_class_mapping", {"category":category, "vendor_id": "tuya"}, json_out=True, none_if_eof=True)
    if dev_class==None:
        return None

    result=dev_class[0]['class_id']
    return result

def get_device(devices, device_id):
    for device in devices:
        if device['id']==device_id:
            return device

    return None

def create_client():
    client=RestApiClient(root_url=CONFIG['default']['restapi']['url'])
    client.login(CONFIG['default']['restapi']['user'],CONFIG['default']['restapi']['password'])
    return client

def logoff_client(client):
    client.logoff()


if __name__=='__main__':
    main()



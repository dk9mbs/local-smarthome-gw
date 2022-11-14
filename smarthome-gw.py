#!/usr/bin/python3
from flask import Flask
import tinytuya
from clientlib import RestApiClient
from config import CONFIG

app = Flask(__name__)

class DeviceRoutingNotFound(Exception):
    pass

class DeviceNotFound(Exception):
    pass

class DeviceAttributeKeyNotFound(Exception):
    pass

#print(tinytuya.deviceScan())

@app.route("/<device_alias>/<attribute>/<value>", methods=['POST','GET'])
def send_command(device_alias, attribute, value):
    client=__create_client()

    rs=__retrive_device(client, device_alias)
    device_attribute_key=__get_device_attribute_key(client, attribute, rs['class_id'])

    if rs!=None and (rs['vendor_id']).upper()=='TUYA' and (rs['class_id']).upper()=='BULB':
        d = tinytuya.BulbDevice(rs['id'], rs['address'], rs['local_key'], dev_type='default')
        d.set_version(float(rs['version']))

        key_value=False
        if value=='on':
            key_value=True

        d.set_value(device_attribute_key,key_value)

    elif rs!=None and (rs['vendor_id']).upper()=='TUYA' and (rs['class_id']).upper()=='OUTLET':
        d = tinytuya.OutletDevice(rs['id'], rs['address'], rs['local_key'], dev_type='default')
        d.set_version(float(rs['version']))

        key_value=False
        if value=='on':
            key_value=True
        print(device_attribute_key)
        d.set_value(device_attribute_key,key_value)
    else:
        print("No device found")

    __logoff_client(client)

    return f"OK"


def __retrive_device(client, device_alias):
    rs=client.read_multible("iot_device_routing", {"internal_device_id": f"{device_alias}" }, json_out=True, none_if_eof=True)
    if rs == None:
        raise DeviceRoutingNotFound(f"{device_alias}")

    rs=client.read_multible("iot_device", {"id": f"{rs[0]['external_device_id']}"}, json_out=True, none_if_eof=True)

    if rs==None:
        raise DeviceNotFound(f"{rs[0]['external_device_id']}")

    return rs[0]


def __get_device_attribute_key(client, attribute, class_id):
    rs=client.read_multible("iot_device_attribute",{"name":f"{attribute}", "class_id": f"{class_id}"}, json_out=True, none_if_eof=True)

    if rs==None:
        raise DeviceAttributeKeyNotFound(f"attribute:{attribute} class_id:{class_id}")

    return rs[0]['device_attribute_key']

def __create_client():
    client=RestApiClient(root_url=CONFIG['default']['restapi']['url'])
    client.login(CONFIG['default']['restapi']['user'],CONFIG['default']['restapi']['password'])
    return client

def __logoff_client(client):
    client.logoff()

if __name__ == '__main__':
    #logger.info(f"Port.......: {AppInfo.get_server_port()}")
    #logger.info(f"Host.......: {AppInfo.get_server_host()}")
    #logger.info(f"Pluginroot.: {AppInfo.get_plugin_root()}")
    app.run(debug=True, host='127.0.0.1', port=5001)


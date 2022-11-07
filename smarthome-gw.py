#!/usr/bin/python3
from flask import Flask
import tinytuya
from clientlib import RestApiClient
from config import CONFIG

app = Flask(__name__)

#print(tinytuya.deviceScan())

@app.route("/<device_alias>/<id>/<value>", methods=['POST','GET'])
def send_command(device_alias, id, value):
    client=__create_client()

    rs=__retrive_device(client, device_alias)

    if rs!=None and (rs['vendor_id']).upper()=='TUYA' and (rs['class_id']).upper()=='BULB':
        d = tinytuya.BulbDevice(rs['id'], rs['address'], rs['local_key'], dev_type='default')
        d.set_version(float(rs['version']))

        key_value=False
        if value=='on':
            key_value=True

        d.set_value(id,key_value)


    __logoff_client(client)

    return f"OK"


def __retrive_device(client, device_alias):
    fetch=f"""
    <restapi type="select">
        <table name="iot_device"/>
        <comment text="from smarthome.py"/>
        <filter type="OR">
            <condition field="alias" value="{device_alias}" operator="="/>
        </filter>
    </restapi>
    """
    rs=client.read_multible("iot_device", fetch, json_out=True, none_if_eof=True)
    if rs!=None:
        return rs[0]
    else:
        return None


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


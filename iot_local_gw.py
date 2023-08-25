#!/usr/bin/python3
from flask import Flask, abort, Response
import tinytuya
import json
import traceback

from clientlib import RestApiClient
from config import CONFIG
from core.log import create_logger
from core.appinfo import AppInfo
from plugins.tuya_common_lib import TuyaDevice
from plugins.tuya_exceptions import TuyaDeviceClassNotImplemented, DeviceRoutingNotFound, DeviceNotFound, DeviceAttributeKeyNotFound

AppInfo.init(__name__, CONFIG['default'])
app = AppInfo.get_app()

tinytuya.set_debug(False)
logger=create_logger(__name__)

def start_mqtt():
    import paho.mqtt.client as mqtt

    def on_connect(client, userdata, flags, rc):
        topic=AppInfo.get_current_config("mqtt","topic", None, exception=True)

        create_logger(__name__).info(f"MQTT Connect with result code:{str(rc)}")
        client.subscribe(topic)
        create_logger(__name__).info("connected!")
        
    def on_message(client, userdata, msg):
        try:
            print(msg)
            message=json.loads(msg.payload)
            session_id=message['session_id']
            internal_device_id=message['internal_device_id']
            attribute=message['attribute']
            value=message['value']

            client=_create_client()
            logger.warning("After create client")

            rs=_retrive_device(client, internal_device_id)
            device_attribute_key, device_attribute_value=_get_device_attribute(client, attribute, rs['class_id'], value)
            logger.warning("After retrive data")

            if rs!=None and (rs['vendor_id']).upper()=='TUYA':
                d=TuyaDevice(rs['class_id'], rs['id'], rs['address'], rs['local_key'], 'default')
                d.create()
                d.set_version(float(rs['version']))
                d.set_value(device_attribute_key, device_attribute_value)

            else:
                print("No device found")

            _logoff_client(client)


        except Exception as e:
            create_logger(__name__).error(e.__traceback__)
            traceback.print_exc()
        

    username=AppInfo.get_current_config("mqtt", "username","")
    password=AppInfo.get_current_config("mqtt", "password", "")
    host=AppInfo.get_current_config("mqtt", "host", "example.com")
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(username, password=password)
    client.connect(host, 1883, 60)
    #client.loop_forever()
    client.loop_start()


@app.route("/<session_id>/<internal_device_id>/<attribute>/<value>", methods=['POST','GET'])
def send_command(session_id, internal_device_id, attribute, value):
    try:
        logger.warning(f"Start request ... {internal_device_id} {attribute} {value}")
        client=_create_client()
        logger.warning("After create client")

        rs=_retrive_device(client, internal_device_id)
        device_attribute_key, device_attribute_value=_get_device_attribute(client, attribute, rs['class_id'], value)
        logger.warning("After retrive data")

        if rs!=None and (rs['vendor_id']).upper()=='TUYA':
            d=TuyaDevice(rs['class_id'], rs['id'], rs['address'], rs['local_key'], 'default')
            d.create()
            d.set_version(float(rs['version']))
            d.set_value(device_attribute_key, device_attribute_value)

        else:
            print("No device found")

        _logoff_client(client)

        return Response(status=200)

    except (DeviceRoutingNotFound,DeviceNotFound,DeviceAttributeKeyNotFound,TuyaDeviceClassNotImplemented) as err:
        logger.exception(f"{err}")
        abort(404,f"{err}")
    except Exception as err:
        logger.exception(f"{err}")
        abort(500,f"{err}")


def _retrive_device(client, device_alias):
    rs=client.read_multible("iot_device_routing", {"internal_device_id": f"{device_alias}" }, json_out=True, none_if_eof=True)
    if rs == None:
        raise DeviceRoutingNotFound(f"{device_alias}")

    rs=client.read_multible("iot_device", {"id": f"{rs[0]['external_device_id']}"}, json_out=True, none_if_eof=True)

    if rs==None:
        raise DeviceNotFound(f"{rs[0]['external_device_id']}")

    return rs[0]


def _get_device_attribute(client, attribute, class_id, value):
    rs=client.read_multible("iot_device_attribute",{"name":f"{attribute}", "class_id": f"{class_id}"}, json_out=True, none_if_eof=True)

    if rs==None:
        raise DeviceAttributeKeyNotFound(f"attribute:{attribute} class_id:{class_id}")

    if rs[0]['is_boolean']==-1:
        if value=='on':
            value=True
        else:
            value=False

    return (rs[0]['device_attribute_key'],value)

def _create_client():
    client=AppInfo.create_restapi_client()
    return client

def _logoff_client(client):
    client.logoff()


@app.before_first_request
def start_monitor():
    from time import sleep
    from threading import Thread
    from plugins.tuya_device_monitor import TuyaDeviceMonitor
    from plugins.tuya_device_scanner import TuyaDeviceScanner

    def run_monitor():
        sleep(5)
        client=AppInfo.create_restapi_client()

        tuya_mon=TuyaDeviceMonitor()
        tuya_mon.execute(client)

    def run_scanner():
        sleep(6)
        client=AppInfo.create_restapi_client()

        tuya_scan=TuyaDeviceScanner()
        tuya_scan.execute(client)

    print("starting the main threads")
    t_mon = Thread(target=run_monitor)
    t_mon.setDaemon(True)
    t_mon.start()

    t_scan = Thread(target=run_scanner)
    t_scan.setDaemon(True)
    t_scan.start()
    print("main threads running")


if __name__ == '__main__':
    start_mqtt()
    start_monitor()
    app.run(debug=True, host=AppInfo.get_server_host(), port=AppInfo.get_server_port())

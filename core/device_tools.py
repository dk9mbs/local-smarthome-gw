import paho.mqtt.client as mqtt
import json

from core.log import create_logger
from core.appinfo import AppInfo

logger=create_logger(__name__)

def mqtt_pub(internal_device_id,external_device_id, channel, value):
    username=AppInfo.get_current_config(section='mqtt', key='username', default='username', exception=True)
    password=AppInfo.get_current_config(section='mqtt', key='password', default='password', exception=True)
    host=AppInfo.get_current_config(section='mqtt', key='host', default='example.com', exception=True)
    port=AppInfo.get_current_config(section='mqtt', key='port', default='1883', exception=True)
    port=1883

    client=mqtt.Client()
    client.username_pw_set(username=username, password=password)
    client.connect(host, port)

    payload=json.dumps({"internal_device_id":internal_device_id,
        "external_device_id":external_device_id,
        "value":value, "channel": channel})

    topic=f"restapi/extension/iot/device/{internal_device_id}"
    client.publish(topic, payload, retain=True)
    client.disconnect()


def set_device_attribute_value(client, device_id,device_class_id, key, value):

    rs=client.read_multible("iot_device_attribute",{"device_attribute_key":key, "vendor_id":"tuya", "class_id": device_class_id},
        json_out=True, none_if_eof=True)

    rs_routing=client.read_multible("iot_device_routing",{"external_device_id":device_id},
        json_out=True, none_if_eof=True)

    if rs==None:
        return

    data={"device_attribute_id": rs[0]['id'],"device_id": device_id}
    values=client.read_multible("iot_device_attribute_value", data, json_out=True, none_if_eof=True)

    if rs[0]['is_boolean']!=0:
        if value==True:
            value="on"
        else:
            value="off"

    if rs_routing!=None:
        mqtt_pub(rs_routing[0]['internal_device_id'], rs_routing[0]['external_device_id'], 0, value)
    else:
        logger.info(f"No routing for device found: {device_id}")

    if values==None:
        data={
        "device_id": device_id,
        "value": value,
        "device_attribute_id": rs[0]['id'],
        }
        result=client.create("iot_device_attribute_value",data, json_out=True)
    else:
        data={
        "value": value,
        }
        result=client.update("iot_device_attribute_value",values[0]['id'], data, json_out=True)


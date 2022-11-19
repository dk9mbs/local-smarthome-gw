from core.log import create_logger

logger=create_logger(__name__)


def set_device_attribute_value(client, device_id,device_class_id, key, value):

    rs=client.read_multible("iot_device_attribute",{"device_attribute_key":key, "vendor_id":"tuya", "class_id": device_class_id},
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


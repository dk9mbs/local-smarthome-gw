#!/usr/bin/python3
from flask import Flask, abort
import tinytuya
from threading import Thread

from clientlib import RestApiClient
from config import CONFIG
from core.log import create_logger
from core.device_tools import set_device_attribute_value
from tuya_scan import main as scan_main

app = Flask(__name__)
logger=create_logger(__name__)

class TuyaDeviceMonitor:
    def __init__(self):
        self._threads=[]

    def execute(self, client):
        logger.warning("starting threads")
        devices=client.read_multible("iot_device",{"vendor_id": "tuya"}, json_out=True, none_if_eof=False)

        for device in devices:
            d = tinytuya.OutletDevice(device['id'], device['address'], device['local_key'])
            d.set_version(3.3)
            d.set_socketPersistent(True)

            t=Thread(target=self.__monitor_device, args=(client,device['id'],device['class_id'], d))
            t.start()

            self._threads.append(t)

        logger.warning("Threads started")

    def __monitor_device(self, client, device_id, device_class_id, device):
        payload = device.generate_payload(tinytuya.DP_QUERY)
        device.send(payload)

        while(True):
            data = device.receive()
            if data != None:
                logger.warning(f"Data from device {device_id}=>{data}")
                if 'dps' in data:
                    for key, value in data['dps'].items():
                        set_device_attribute_value(client, device_id, device_class_id, key, value)

            payload = device.generate_payload(tinytuya.HEART_BEAT)
            device.send(payload)






#!/usr/bin/python3
from flask import Flask, abort
import tinytuya
from threading import Thread
import time

#from clientlib import RestApiClient
#from config import CONFIG
from core.log import create_logger
#from core.device_tools import set_device_attribute_value
from tuya_scan import main as scan_main

app = Flask(__name__)
logger=create_logger(__name__)

class TuyaDeviceScanner:
    def __init__(self):
        pass

    def execute(self, client):
        while(True):
            logger.warning("scanning devices ...")
            scan_main()
            logger.warning("devices scanned")
            time.sleep(600.0)







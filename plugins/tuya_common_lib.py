import tinytuya
from plugins.tuya_exceptions import TuyaDeviceClassNotImplemented

class TuyaDevice():
    def __init__(self, class_id, id, address, local_key, dev_type='default'):
        self.__device=None
        self.__class_id=class_id
        self.__id=id
        self.__address=address
        self.__local_key=local_key
        self.__dev_type=dev_type

    def create(self):
        if self.__class_id.upper()=='BULB':
            d = tinytuya.BulbDevice(self.__id, self.__address, self.__local_key, self.__dev_type)
        elif class_id.upper()=='OUTLET':
            d = tinytuya.OutletDevice(self.__id, self.__address, self.__local_key, self.__dev_type)
        else:
            raise TuyaDeviceClassNotImplemented(f"TUYA class_id not implemented: {class_id}")

        self.__device=d


    def set_version(self, version):
        self.__device.set_version(float(version))

    def set_value(self, attribute, value):
        self.__device.set_value(attribute, value)


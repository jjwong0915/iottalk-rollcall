# DAI2.py #coding=utf-8 -- new version of Dummy Device DAI.py, modified by tsaiwn@cs.nctu.edu.tw
import os
import time
import uuid
from bluetooth.ble import BeaconService
from django.core.management import base
from dummy_device import dan


class Beacon:
    def __init__(self, data, address):
        self._uuid = data[0]
        self._major = data[1]
        self._minor = data[2]
        self._power = data[3]
        self._rssi = data[4]
        self._address = address


class Command(base.BaseCommand):
    def handle(self, *args, **options):
        iottalk = dan.Iottalk(
            dm_name="Dummy_Device",
            df_list=["Dummy_Sensor", "Dummy_Control"],
            d_name="Rollcall-Sensor-1",
            mac=uuid.uuid4().hex,
        )
        iottalk.device_registration_with_retry(os.getenv("IOTTALK_ENDPOINT"))
        service = BeaconService()
        try:
            while True:
                devices = service.scan(2)
                for address, data in devices.items():
                    student = Beacon(data, address)
                    if student._rssi > -40:
                        print("Get UUID: ", student._uuid)
                        iottalk.push("Dummy_Sensor", str(student._uuid))
                time.sleep(0.5)
        finally:
            iottalk.deregister()

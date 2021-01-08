import os
import time
import uuid
from django.core.management import base
from ... import models
from .dummy_device import dan


class Command(base.BaseCommand):
    def handle(self, *args, **options):
        iottalk = dan.Iottalk(
            dm_name="Dummy_Device",
            df_list=["Dummy_Control", "Dummy_Sensor"],
            d_name="rollcall-collector",
            mac=uuid.uuid4().hex,
        )
        iottalk.device_registration_with_retry(os.getenv("IOTTALK_ENDPOINT"))
        try:
            while True:
                data = iottalk.pull("Dummy_Control")
                if data:
                    student_id = data[0]
                    _, created = models.Attendance.objects.get_or_create(
                        student_id=student_id,
                        confirmed=False,
                    )
                    if created:
                        iottalk.push("Dummy_Sensor", student_id)
                time.sleep(0.2)
        finally:
            iottalk.deregister()

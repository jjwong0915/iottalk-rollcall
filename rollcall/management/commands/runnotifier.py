import linebot
import os
import time
import uuid
from django.core.management import base
from linebot import models

from .dummy_device import dan


class Command(base.BaseCommand):
    def handle(self, *args, **options):
        iottalk = dan.Iottalk(
            dm_name="Dummy_Device",
            df_list=["Dummy_Control"],
            d_name="rollcall-notifier",
            mac=uuid.uuid4().hex,
        )
        iottalk.device_registration_with_retry(os.getenv("IOTTALK_ENDPOINT"))
        line_api = linebot.LineBotApi(os.getenv("LINE_ACCESS_TOKEN"))
        try:
            while True:
                data = iottalk.pull("Dummy_Control")
                if data:
                    line_api.broadcast(models.TextSendMessage(data[0]))
                time.sleep(0.2)
        finally:
            iottalk.deregister()

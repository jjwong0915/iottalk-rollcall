import requests
import socket
import time
import threading
from . import csmapi


class Iottalk:
    def __init__(self, dm_name, df_list, d_name, mac):
        self.profile = {
            "dm_name": dm_name,
            "u_name": "yb",
            "is_sim": False,
            "df_list": df_list,
            "d_name": d_name,
        }
        self.state = "SUSPEND"
        self.selected_df = []
        self.timestamp = {}
        self.MAC = mac
        self.thx = None

    def ControlChannel(self):
        print("Device state:", self.state)
        NewSession = requests.Session()
        control_channel_timestamp = None
        while True:
            time.sleep(2)
            try:
                CH = csmapi.pull(self.MAC, "__Ctl_O__", NewSession)
                if CH != []:
                    if control_channel_timestamp == CH[0][0]:
                        continue
                    control_channel_timestamp = CH[0][0]
                    cmd = CH[0][1][0]
                    if cmd == "RESUME":
                        print("Device state: RESUME.")
                        self.state = "RESUME"
                    elif cmd == "SUSPEND":
                        print("Device state: SUSPEND.")
                        self.state = "SUSPEND"
                    elif cmd == "SET_DF_STATUS":
                        csmapi.push(
                            self.MAC,
                            "__Ctl_I__",
                            [
                                "SET_DF_STATUS_RSP",
                                {"cmd_params": CH[0][1][1]["cmd_params"]},
                            ],
                            NewSession,
                        )
                        DF_STATUS = list(CH[0][1][1]["cmd_params"][0])
                        self.selected_df = []
                        index = 0
                        self.profile["df_list"] = csmapi.pull(
                            self.MAC, "profile"
                        )[
                            "df_list"
                        ]  # new
                        for STATUS in DF_STATUS:
                            if STATUS == "1":
                                self.selected_df.append(
                                    self.profile["df_list"][index]
                                )
                            index = index + 1
            except Exception as e:
                print("Control error:", e)
                if str(e).find("mac_addr not found:") != -1:
                    print("Reg_addr is not found. Try to re-register...")
                    self.device_registration_with_retry()
                else:
                    print("ControlChannel failed due to unknow reasons.")
                    time.sleep(1)

    def get_mac_addr(self):
        from uuid import getnode

        mac = getnode()
        mac = "".join(("%012X" % mac)[i : i + 2] for i in range(0, 12, 2))
        return mac

    def detect_local_ec(self):
        EASYCONNECT_HOST = None

        UDP_IP = ""
        UDP_PORT = 17000
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((UDP_IP, UDP_PORT))
        while EASYCONNECT_HOST is None:
            print("Searching for the IoTtalk server...")
            data, addr = s.recvfrom(1024)
            if str(data.decode()) == "easyconnect":
                EASYCONNECT_HOST = "http://{}:9999".format(addr[0])
                csmapi.ENDPOINT = EASYCONNECT_HOST
                # print('IoTtalk server = {}'.format(csmapi.ENDPOINT))

    def register_device(self, addr):
        if csmapi.ENDPOINT is None:
            self.detect_local_ec()

        if addr:
            self.MAC = addr

        for i in self.profile["df_list"]:
            self.timestamp[i] = ""

        print("IoTtalk Server = {}".format(csmapi.ENDPOINT))
        self.profile["d_name"] = csmapi.register(self.MAC, self.profile)
        print("This device has successfully registered.")
        print("Device name = " + self.profile["d_name"])

        if self.thx is None:
            print("Create control threading")
            thx = threading.Thread(
                target=self.ControlChannel
            )  # for control channel
            thx.daemon = True  # for control channel
            thx.start()  # for control channel

    def device_registration_with_retry(self, URL=None, addr=None):
        if URL:
            csmapi.ENDPOINT = URL
        success = False
        while not success:
            try:
                self.register_device(addr)
                success = True
            except Exception as e:
                print("Attach failed: "),
                print(e)
            time.sleep(1)

    def pull(self, FEATURE_NAME):
        if self.state == "RESUME":
            data = csmapi.pull(self.MAC, FEATURE_NAME)
        else:
            data = []

        if data != []:
            if self.timestamp[FEATURE_NAME] == data[0][0]:
                return None
            self.timestamp[FEATURE_NAME] = data[0][0]
            if data[0][1] != []:
                return data[0][1]
            else:
                return None
        else:
            return None

    def push(self, FEATURE_NAME, *data):
        if self.state == "RESUME":
            return csmapi.push(self.MAC, FEATURE_NAME, list(data))
        else:
            return None

    def get_alias(self, FEATURE_NAME):
        try:
            alias = csmapi.get_alias(self.MAC, FEATURE_NAME)
        except Exception:
            return None
        else:
            return alias

    def set_alias(self, FEATURE_NAME, alias):
        try:
            alias = csmapi.set_alias(self.MAC, FEATURE_NAME, alias)
        except Exception:
            return None
        else:
            return alias

    def deregister(self):
        return csmapi.deregister(self.MAC)

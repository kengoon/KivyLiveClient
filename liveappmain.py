"""
HotReloader
-----------
Uses kaki module for Hot Reload (limited to some uses cases).
Before using, install kaki by `pip install kaki`

"""

import os
from threading import Thread
import socket
from kaki.app import App as HotReloaderApp  # NOQA: E402
from kivy.factory import Factory
from kivy.logger import LOG_LEVELS, Logger  # NOQA: E402
from kivy import platform
from kivy.clock import Clock
from kivy.core.window import Window  # NOQA: E402
from kivymd.app import MDApp  # NOQA: E402
import pickle
# This is needed for supporting Windows 10 with OpenGL < v2.0
from kivymd.toast import toast

if platform == "win":
    os.environ["KIVY_GL_BACKEND"] = "angle_sdl2"
Logger.setLevel(LOG_LEVELS["debug"])


class KivyLive(MDApp, HotReloaderApp):
    DEBUG = 1  # To enable Hot Reload

    # *.kv files to watch
    KV_FILES = [f"libs/libkv/{kv_file}" for kv_file in os.listdir("libs/libkv")]

    # Class to watch from *.py files
    # You need to register the *.py files in libs/uix/baseclass/*.py
    CLASSES = {"Root": "libs.libpy.root", "Home": "libs.libpy.home"}

    # Auto Reloader Path
    AUTORELOADER_PATHS = [
        (".", {"recursive": True}),
    ]

    def __init__(self, **kwargs):
        super(KivyLive, self).__init__(**kwargs)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HEADER_LENGTH = 64
        Window.soft_input_mode = "below_target"
        self.title = "KivyLiveUi"

        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "500"

        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.accent_hue = "500"

        self.theme_cls.theme_style = "Light"

    def build_app(self):  # build_app works like build method
        return Factory.Root()

    def thread_server_connection(self, ip):
        toast(f"establishing connection to {ip}:6050")
        Thread(target=self.connect2server, args=(ip,)).start()

    def connect2server(self, ip):
        try:
            self.client_socket.connect((ip, 6051))
            Clock.schedule_once(lambda x: toast("Connection Established Successfully"))
            Logger.info(f"{ip}>6050: Connection Established")
            Thread(target=self.listen_4_update).start()
        except (OSError, socket.gaierror) as e:
            exception = e
            Clock.schedule_once(lambda x: toast(f"{exception}"))
        except:
            pass

    def listen_4_update(self):
        _header = self.client_socket.recv(self.HEADER_LENGTH)
        load_initial_code = pickle.loads(self.client_socket.recv(int(_header)))
        for i in load_initial_code:
            file_path = os.path.split(i)[0]
            try:
                os.makedirs(file_path)
            except (FileExistsError, FileNotFoundError) as e:
                Logger.debug(f"{e} : Ignore this")
            if os.path.split(i)[1] == "main.py":
                continue
            with open(
                    os.path.join(file_path, os.path.split(i)[1]), "wb" if type(load_initial_code[i]) == bytes else "w"
            ) as f:
                f.write(load_initial_code[i])
        try:
            while True:
                header = self.client_socket.recv(self.HEADER_LENGTH)
                if not len(header):
                    Clock.schedule_once(lambda x: toast("SERVER DOWN: Shutting down the connection"))
                    Logger.info("SERVER DOWN: Shutting down the connection")
                    break
                message_length = int(header)
                code_data = self.client_socket.recv(message_length).decode()
                self.update_code(code_data)
        except:
            Clock.schedule_once(lambda x: toast("SERVER DOWN: Shutting down the connection"))
            Logger.info("SERVER DOWN: Shutting down the connection")

    @staticmethod
    def update_code(code_data):
        # write code
        file = code_data["data"]["file"]
        with open(file, "w") as f:
            f.write(code_data["data"]["code"])
        Logger.info(f"FILE UPDATE: {file} was updated by {code_data['address']}")
        Clock.schedule_once(lambda x: toast(f"{file} was updated by {code_data['address']}"))


if __name__ == "__main__":
    KivyLive().run()

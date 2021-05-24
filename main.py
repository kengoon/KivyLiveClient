import pickle
from json import dumps
from time import sleep
import os
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from threading import Thread
import logging
import sys
import socket
import errno
from kivy import Logger
from _thread import interrupt_main

# --------Binary File Checker----------#
text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
is_binary = lambda byte: bool(byte.translate(None, text_chars))
# --------Binary File Checker----------#


class KivyFileListener(FileSystemEventHandler):
    def __init__(self):
        self.client_socket = KivyLiveClient()
        self.filepath = ""

    def on_any_event(self, event):
        pass

    def on_modified(self, event):
        filename = os.path.basename(self.filepath).strip("~")
        if filename.endswith("main.py") or not self.filepath:
            return
        binary = is_binary(open(self.filepath, "rb").read(1024))
        with open(self.filepath, "rb" if binary else "r") as file:
            code_data = pickle.dumps({"file": os.path.relpath(self.filepath), "code": file.read()})
            self.client_socket.send_code(
                f"{len(code_data):<{self.client_socket.HEADER_LENGTH}}".encode("utf-8") + code_data
            )
            #self.client_socket.send_code(f"hello world".encode("utf-8"))

    def on_created(self, event):
        self.filepath = event.src_path.strip("~")

    def on_closed(self, event):
        pass

    def on_moved(self, event):
        pass

    def on_deleted(self, event):
        pass


class KivyLiveClient:
    def __init__(self, **kwargs):
        self.HEADER_LENGTH = 64
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("0.0.0.0", 6051))
        # self.client_socket.setblocking(False)
        Thread(target=self.recv_code).start()

    def send_code(self, code_data):
        self.client_socket.send(code_data)

    def recv_code(self):
        _header = self.client_socket.recv(self.HEADER_LENGTH)
        load_initial_code = pickle.loads(self.client_socket.recv(int(_header)))
        for i in load_initial_code:
            file_path = os.path.split(i)[0]
            try:
                os.makedirs(file_path)
            except FileExistsError as e:
                Logger.debug(f"{e} : Ignore this")
            if os.path.split(i)[1] == "main.py":
                with open(
                        os.path.join(file_path, "liveappmain.py"),
                        "wb" if type(load_initial_code[i]) == bytes else "w"
                ) as f:
                    f.write(load_initial_code[i])
            else:
                with open(
                        os.path.join(file_path, os.path.split(i)[1]),
                        "wb" if type(load_initial_code[i]) == bytes else "w"
                ) as f:
                    f.write(load_initial_code[i])
        try:
            while True:
                header = self.client_socket.recv(self.HEADER_LENGTH)
                if not len(header):
                    Logger.info("SERVER DOWN: Shutting down the connection")
                    break
                message_length = int(header)
                code_data = self.client_socket.recv(message_length).decode()
                self.update_code(code_data)
            interrupt_main()
        except KeyboardInterrupt:
            pass

        except:
            Logger.info("SERVER DOWN: Shutting down the connection")
            interrupt_main()

    @staticmethod
    def update_code(code_data):
        # write code
        file = code_data["data"]["file"]
        with open(file if file != "main.py" else "liveappmain.py", "w") as f:
            f.write(code_data["data"]["code"])
        Logger.info(f"FILE UPDATE: {file} was updated by {code_data['address']}")


if __name__ == "__main__":
    try:
        path = sys.argv[1]
    except IndexError:
        logging.error("add a directory. e.g: python main.py /path/to/file")
        exit()
    observer = Observer()
    observer.schedule(KivyFileListener(), path=path, recursive=True)
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

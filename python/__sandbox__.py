# https://docs.python.org/3/library/struct.html
import os
import threading
import _thread
import enum
import socket
import struct
import sys
from .header_message import HeaderMessage

_BYTES_ORDER_ = sys.byteorder

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)


class NetData(enum.Enum):
    PORT = 18813
    IP = "127.0.0.1"


def client_command(command):
    if command.startswith("<command>"):
        try:
            exec(command.replace("<command>", ""))
        except:
            logger.exception("Fail excecuting command")

    return command


def server_command(host, message):
    if message == "create a ball":
        return "<command>import hou;hou.node('/obj').createNode('geo')"

    return None


class HouNetServer(object):
    # https://www.geeksforgeeks.org/socket-programming-multi-threading-python/
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.bind((NetData.IP.value,
                            NetData.PORT.value))
        except OSError as e:
            logger.error(e)
            raise

        self.sock.listen(5)
        self._connections = dict()
        self.lock = threading.Lock()

    def _thread_server(self, sock, address):
        address_name = "%s:%s" % address
        try:
            host = HeaderMessage().collect_message(sock).message_to_str()
            # lock and save adress and sock
            with self.lock:
                self._connections[address_name] = sock

            hdr_messg = HeaderMessage()
            hdr_messg.set_message(
                "Welcome %s user. host: %s" % (address_name, host))
            sock.sendall(hdr_messg.to_bytes())
            while True:
                hdr_messg.collect_message(sock)
                if not hdr_messg:
                    print("Close connection with, %s" % sock)
                    break
                message = hdr_messg.message_to_str()
                logger.debug("SERVER: %s" % message)

                cmd = server_command(host, message)
                if cmd:
                    sock.sendall(HeaderMessage().set_message(cmd).to_bytes())

        except:
            logger.exception("SERVER ERROR")

        finally:
            if address_name in self._connections:
                with self.lock:
                    self._connections.pop(address_name)

            sock.sendall(HeaderMessage().to_bytes())
            sock.close()

    def run(self):
        while True:
            connection, address = self.sock.accept()

            logger.info("Accepted from: %s, %s" % address)
            threading.Thread(target=self._thread_server,
                             args=(connection, address)).start()

        self.sock.close()

    @staticmethod
    def treaded_server():
        server = HouNetServer()
        thread = threading.Thread(
            target=server.run
        )
        # thread.daemon = True
        thread.start()

        return thread, server


class HouNetClient(object):

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, address=None, host="houdini"):
        self.sock.connect((NetData.IP.value,
                           NetData.PORT.value))

        self.sock.sendall(HeaderMessage().set_message(host).to_bytes())

        thread = threading.Thread(
            target=self._thread_listen
        )
        thread.daemon = True
        thread.start()

    def _thread_listen(self):
        mssg_hdr = HeaderMessage()
        while True:
            mssg_hdr.collect_message(self.sock)
            if not mssg_hdr:
                break

            logger.debug("CLIENT: %s" % client_command(
                mssg_hdr.message_to_str())
                         )

        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def send_message(self, message="print(\"Hello pepe\")"):
        hdr_mssg = HeaderMessage()
        hdr_mssg.set_message(message)
        self.sock.sendall(HeaderMessage().set_message(message).to_bytes())

    def close(self):
        self.sock.sendall(HeaderMessage().to_bytes())


# def open_hou_ports():
#     port = HouNetClient.HOU_PORT
#     try:
#         hrpyc.start_server(port)
#     except OSError as e:
#         logger.error(e)
#
#     return port


if __name__ == "__main__":
    HouNetServer().run()

"""
python ./site/_abs/houdini/__hou_net__.py

from _abs.houdini import __hou_net__
cl = __hou_net__.HouNetClient()
cl.connect()
cl.send_message("create a ball")
"""
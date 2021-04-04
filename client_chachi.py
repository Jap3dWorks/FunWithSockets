# https://realpython.com/python-sockets/
# https://github.com/realpython/materials/tree/master/python-sockets-tutorial
import sys
import os
import socket
import selectors
import threading
import queue
import subprocess
import time

import logging


os.environ["DEBUG_LEVEL"] = str(logging.DEBUG)

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(int(os.getenv("DEBUG_LEVEL", logging.INFO)))


_HEADER_BYTES_ = 2
_BYTES_ORDER_ = repr(sys.byteorder)


class SData(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class SockClient(object):
    _count = 0

    def __init__(self, server, addr):
        self._server = server
        self._addr = addr

        # start socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect_ex((self._server, self._addr))

        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.server_message = queue.Queue()

        # unique object id
        self.id = SockClient._count
        SockClient._count += 1

    def send_data(self, message):
        self.out_messages.append(message)
        MSGLEN = len(message)

        # headder
        message = (MSGLEN).to_bytes(2, _BYTES_ORDER_) + message

        while message:
            sent = self.sock.send(message)
            if sent == 0:
                raise RuntimeError("Socket connection broken")

            # remove sended message
            message = message[sent:]

    def _start_listen_server(self):
        thrd = threading.Thread(target=self.receive_data)
        thrd.daemon = True
        thrd.start()

    def receive_data(self):
        msg = b""
        # get size in hexadecimal
        # TODO: Byte order
        body_length = b""
        while len(body_length) < _HEADER_BYTES_:
            body_length += self.sock.recv(_HEADER_BYTES_ - len(body_length))

        body_length = int.from_bytes(body_length, _BYTES_ORDER_, signed=False)
        logger.debug(body_length)

        while len(msg) < body_length:
            rec_tmp = self.sock.recv(body_length - len(msg))
            logger.debug(rec_tmp)
            msg += rec_tmp

        self.server_message.put(msg)


class ConsoleInput(object):
    def __init__(self):
        self.message_queue = queue.Queue()
        self._start_thread()
    # console input
    def add_input(self):
        while True:
            self.message_queue.put(sys.stdin.readline())

    def _start_thread(self):
        input_thread = threading.Thread(target=self.add_input)
        input_thread.daemon = True
        input_thread.start()


class ClientService(object):
    def __init__(self, server, addr):
        self.sock_client = SockClient(server, addr)
        self.console_input = ConsoleInput()

    def run(self):
        try:
            while True:
                if not self.sock_client.server_message.empty():
                    logger.debug(self.sock_client.server_message.get())

                if not self.console_input.message_queue.empty():
                    message = self.console_input.message_queue.get()
                    self.sock_client.send_data("Client: " + message)

        except KeyboardInterrupt as e:
            logger.error(e)
            sys.exit(0)



if __name__ == "__main__":
    pass
# python client_chachi.py 83.47.119.77 8000 2
# HOST = "83.47.119.77"
# PORT = 8000

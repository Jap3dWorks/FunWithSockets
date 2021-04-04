# https://realpython.com/python-sockets/
# https://github.com/realpython/materials/tree/master/python-sockets-tutorial
import sys
import os
import socket
import threading
import queue
import logging
import signal

os.environ["DEBUG_LEVEL"] = str(logging.DEBUG)

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(int(os.getenv("DEBUG_LEVEL", logging.INFO)))


_HEADER_BYTES_ = 2
_BYTES_ORDER_ = sys.byteorder


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

        self.server_message = queue.Queue()
        self._server_thread = None
        self._stop_thread = False
        self._start_listen_server()

        # unique object id
        self.id = SockClient._count
        SockClient._count += 1

    def send_data(self, message):
        message = message.encode("utf-8")
        message_length = len(message)

        # header
        message = (message_length).to_bytes(_HEADER_BYTES_, _BYTES_ORDER_) + message

        while message:
            sent = self.sock.send(message)
            if sent == 0:
                raise RuntimeError("Socket connection broken")

            message = message[sent:]

    def _start_listen_server(self):
        self._server_thread = threading.Thread(target=self.receive_data)
        self._server_thread.daemon = True
        self._server_thread.start()

    def receive_data(self):
        # TODO: Byte order
        while self.is_running:

            body_length = b""
            while len(body_length) < _HEADER_BYTES_:
                # Function waits here to a new header.
                body_length += self.sock.recv(_HEADER_BYTES_ - len(body_length))

            body_length = int.from_bytes(body_length, _BYTES_ORDER_, signed=False)

            message = b""
            while len(message) < body_length:
                rec_tmp = self.sock.recv(body_length - len(message))
                message += rec_tmp

            self.server_message.put(message)

    @property
    def is_running(self):
        return not self._stop_thread

    def close(self):
        self._stop_thread = True
        self._server_thread.join()
        self.sock.close()


class ConsoleInput(object):
    def __init__(self):
        self.message_queue = queue.Queue()
        self._start_thread()

    # console input
    def add_input(self):
        while True:
            self.message_queue.put(sys.stdin.readline().strip())

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
            while self.sock_client.is_running:
                if not self.sock_client.server_message.empty():
                    logger.info(self.sock_client.server_message.get().decode("utf-8"))

                if not self.console_input.message_queue.empty():
                    message = self.console_input.message_queue.get()
                    if message == "exit()":
                        self.sock_client.close()
                    else:
                        self.sock_client.send_data(message)

        except KeyboardInterrupt as e:
            self.sock_client.close()
            logger.info("Close Client")
            sys.exit(0)


if __name__ == "__main__":
    pass
# python client_chachi.py 83.47.119.77 8000 2
# HOST = "83.47.119.77"
# PORT = 8000

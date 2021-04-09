# https://realpython.com/python-sockets/
# https://github.com/realpython/materials/tree/master/python-sockets-tutorial
import sys
import os
import socket
import threading
import queue
import logging
from python.header_message import HeaderMessage

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(int(os.getenv("DEBUG_LEVEL", logging.INFO)))


# TODO: buscar una forma de escuchar si tengo data pendiente en el socket del cliente

class SockClient(object):

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._is_running = False
        self.server_message = queue.Queue()

    def connect(self, address):
        self.sock.connect(address)
        self._is_running = True

        thread = threading.Thread(
            target=self._thread_listen)

        thread.daemon = True
        thread.start()

    def _thread_listen(self):
        mssg_hdr = HeaderMessage()

        while self._is_running:
            mssg_hdr.collect_message(self.sock)
            if not mssg_hdr:
                self._is_running = False
                break

            self.server_message.put(mssg_hdr.message)

        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def send_data(self, data):
        self.sock.sendall(HeaderMessage().set_message(data).to_bytes())

    def close(self):
        self.sock.sendall(HeaderMessage().to_bytes())

    @property
    def is_running(self):
        return self._is_running


class ConsoleInput(object):
    def __init__(self):
        self._close = False
        self.message_queue = queue.Queue()
        self._start_thread()

    # console input
    def add_input(self):
        while not self._close:
            message = sys.stdin.readline().strip()
            if not message:
                continue
            self.message_queue.put(message)

    def _start_thread(self):
        input_thread = threading.Thread(target=self.add_input)
        input_thread.daemon = True
        input_thread.start()

    def close(self):
        if not self._close:
            self._close = True


class ConsoleClient(object):
    def __init__(self, server, addr):
        self.sock_client = SockClient()
        self.sock_client.connect((server, addr))
        self.console_input = ConsoleInput()
        self.exit_command = "exit"

    def close(self):
        self.sock_client.close()
        self.console_input.close()

    def run(self):
        try:
            while self.sock_client.is_running:
                if not self.sock_client.server_message.empty():
                    logger.info(self.sock_client.server_message.get().decode("utf-8"))

                if not self.console_input.message_queue.empty():
                    message = self.console_input.message_queue.get()
                    if message == self.exit_command:
                        self.close()
                    else:
                        self.sock_client.send_data(message)

        except KeyboardInterrupt as e:
            self.close()
            logger.info("Close Client")


if __name__ == "__main__":
    pass
# python client_chachi.py 83.47.119.77 8000 2
# HOST = "83.47.119.77"
# PORT = 8000

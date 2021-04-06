# https://realpython.com/python-sockets/
# https://github.com/realpython/materials/tree/master/python-sockets-tutorial
import sys
import os
import socket
import threading
import queue
import logging


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(int(os.getenv("DEBUG_LEVEL", logging.INFO)))


_HEADER_BYTES_ = 4
_BYTES_ORDER_ = sys.byteorder
# TODO: Max length of message with the header
_MAX_SIZE_ = (2 ^ (_HEADER_BYTES_ * 8)) - 1


# class HeaderOffsets:
#     type = 0  # 0, 1, 2
#     Size = 1
#     type = 1 + _HEADER_BYTES_
#     
    # name =

# TODO: buscar una forma de escuchar si tengo data pendiente en el socket del cliente


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

        # self.sock.setblocking(False)

        self.server_message = queue.Queue()
        self._server_thread = None
        self._close = False
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
                try:
                    body_length += self.sock.recv(_HEADER_BYTES_ - len(body_length))
                except socket.timeout as e:
                    logger.exception("Fail receiving socket data.")
                    continue

            body_length = int.from_bytes(body_length, _BYTES_ORDER_, signed=False)
            if not body_length:
                logger.info("Break socket loop")
                break

            message = b""
            while len(message) < body_length:
                try:
                    rec_tmp = self.sock.recv(body_length - len(message))
                except socket.timeout as e:
                    logger.exception("Fail receiving socket data.")
                    continue
                if not rec_tmp:
                    self.close()
                    break

                message += rec_tmp

            self.server_message.put(message)

        self._close = True
        self.sock.shutdown(socket.SHUT_RD)
        self.sock.close()

    @property
    def is_running(self):
        return not self._close

    def close(self):
        if not self._close:
            self.send_data("")


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


class ClientService(object):
    def __init__(self, server, addr):
        self.sock_client = SockClient(server, addr)
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

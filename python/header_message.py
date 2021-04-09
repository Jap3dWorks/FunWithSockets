import sys
import os
import threading
import _thread
import enum
import socket
import struct
import logging

_BYTES_ORDER_ = sys.byteorder

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(int(os.getenv("DEBUG_LEVEL", logging.INFO)))


class HeaderMessage(object):
    def __init__(self):
        # if connection must be closed
        self._active = (0).to_bytes(1, _BYTES_ORDER_, signed=False)
        self._title_size = b""
        self._title = b""
        self._message_size = b""
        self._message = b""

    def collect_message(self, sock):
        self._active = self._get_data(sock, 1)
        if not self:
            return self

        self._title_size = self._get_data(sock, 2)
        self._title = self._get_data(
            sock, int.from_bytes(
                self._title_size, _BYTES_ORDER_, signed=False))

        self._message_size = self._get_data(sock, 4)
        self._message = self._get_data(
            sock, int.from_bytes(
                self._message_size, _BYTES_ORDER_, signed=False))

        return self

    def _get_data(self, sock, bsize):
        data = b""
        remain = bsize
        while remain:
            data += sock.recv(remain)
            remain = bsize - len(data)

        return data

    def __bool__(self):
        return bool(int.from_bytes(self._active, _BYTES_ORDER_, signed=False))

    @property
    def message_size(self):
        return int.from_bytes(self._message_size, _BYTES_ORDER_, signed=False)

    @property
    def message(self):
        return self._message

    def set_message(self, message, title=""):
        self._message = message.encode("utf-8")
        self._message_size = \
            len(self._message).to_bytes(4, _BYTES_ORDER_, signed=False)

        self._title = title.encode("utf-8")
        self._title_size = \
            len(self._title).to_bytes(2, _BYTES_ORDER_, signed=False)

        self._active = \
            (1 if message else 0).to_bytes(1, _BYTES_ORDER_, signed=False)

        return self

    def to_bytes(self):
        return self._active + self._title_size + self._title + self._message_size + self._message

    def message_to_str(self):
        return self._message.decode("utf-8")


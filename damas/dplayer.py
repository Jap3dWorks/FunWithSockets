# https://www.mundijuegos.com/multijugador/damas/reglas/
""""
=Server=
00 -> type, (aclaracion || estado tablero || game over || interruption)
0 -> player,  par | impar                 ||     Interruption (0 - 63)
00000 -> Token data size (int 32)         ||

Token data
[0, token, 23] 24 max size

Token
0 -> team
0 -> ciclada
000000 -> 64

=Client=
0 -> type, 0/ jugada                    || 1/ message
0000000 -> movements size  | [abandono] || 0000000 -> message size
                                        || chat message

(000000) 001010 101010

ceil(size * 6 / 8) - bytes a leer
buffer & 111111; buffer > 6;

pos sequence
[byte init, byte, 64, 64, 64] - 12
[64, byte, 64, 64, 64] abandono
"""
from funnet import client_chachi
from funnet import header_message
import os
import sys
import math

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
# logger.setLevel(int(os.getenv("DEBUG_LEVEL", logging.INFO)))
logger.setLevel(logging.DEBUG)


class DPiece(object):
    def __init__(self):
        self._position = 0


class DGame(object):
    pass


class DServerMessage(header_message.AbcMessage):
    CLARIFICATION = 0
    BOARD_STATE = 1
    GAME_OVER = 2
    INTERRUPTION = 3

    def __init__(self):
        super(DServerMessage, self).__init__()

        self._type_bitmask = 192
        self._interruption_header_mask = 63
        self._player_bitmask = 32
        self._size_bitmask = 31

    @property
    def type(self):
        return self.header_to_int() & self._type_bitmask

    @property
    def player(self):
        """Returns 0 or 1"""
        return self.header_to_int() & self._player_bitmask

    @property
    def interruption(self):
        return self.header_to_int() & self._interruption_header_mask


    @property
    def message_size(self):
        """
        returns size of movement buffer.
        Returns:
            int: size of movement buffer
        """
        return self.header_to_int() & self._size_bitmask


class DClientMessage(header_message.AbcMessage):
    MESSAGE = 1
    GAME = 0

    def __init__(self):
        super(DClientMessage, self).__init__()

        self._type_bitmask = 128
        self._size_bitmask = 127

        self._movement_bitmask = 63
        self._movement_offset = 6

    def collect_message(self, sock):
        self._header = self.get_socket_data(sock, 1)
        if not self:
            logger.debug("Null header received: %s" % self._header)
            return self

        self._message = self.get_socket_data(sock, self.message_size)
        return self

    def set_message(self, message, message_type):
        """
        Sets movements message
        Args:
            message: list(int): Movements sequence.
            message_type: int: 0 game, 1 text message
        Returns:
            self: chainable
        """
        if message_type == self.GAME:
            message.reverse()
            bit_message = message[0]

            for move in message[1:]:
                bit_message <<= self._movement_offset
                bit_message |= move

            self._message = bit_message.to_bytes(
                math.ceil(len(message) * 6.0 / 8.0),
                self._byte_order_,
                signed=False)

            header = 0

        else:
            self._message = message.encode("utf-8")
            header = 128

        # header
        header |= len(self._message)  # bytes size
        self._header = header.to_bytes(1, self._byte_order_, signed=False)

        return self

    @property
    def type(self):
        """
        0 Game / 1 Message
        """
        return self.header_to_int() & self._type_bitmask

    @property
    def message_size(self):
        """
        returns size of movement buffer.
        Returns:
            int: size of movement buffer
        """
        return self.header_to_int() & self._size_bitmask

    def to_bytes(self):
        return self._header + self._message

    def message_as_movements(self):
        movements = int.from_bytes(self._message, self._byte_order_, signed=False)

        for _ in range(self.message_size * 8 // 6):
            yield movements & self._movement_bitmask
            movements >>= self._movement_offset

    def message_as_str(self):
        return self._message.decode("utf-8")

    def __bool__(self):
        """Abandono False"""
        return bool(self.message_size)


class BoardGame(object):
    pass


class DClient(client_chachi.ConsoleClient):
    MessageClass = DClientMessage

    def __init__(self, team):
        # TODO: Damas rules
        # TODO: header
        # TODO: origen -> destino message -> destino message 2
        # TODO: comprobar turno
        # TODO: Turn Timer
        # TODO: Simulation
        self._my_turn = False
        self._team = team
        self._game_board = list(range(64))

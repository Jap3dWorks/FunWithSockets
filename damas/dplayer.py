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
0 -> type, jugada                       || message
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


class DPiece(object):
    def __init__(self):
        self._position = 0


class DGame(object):
    pass


class GameMessage(object):
    pass


class BoardGame(object):
    pass


class DClient(client_chachi.ConsoleClient):
    MessageClass = GameMessage

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

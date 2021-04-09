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


class SockServer(object):
    # https://www.geeksforgeeks.org/socket-programming-multi-threading-python/
    def __init__(self, address, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.bind((address, port))
        except OSError as e:
            logger.error(e)
            raise

        self.sock.listen(5)
        self._connections = dict()
        self.lock = threading.Lock()

    def _client_thread(self, sock, address):
        address_name = "%s:%s" % address
        try:
            # lock and save adress and sock
            with self.lock:
                self._connections[address_name] = sock

            hmssg = HeaderMessage()
            hmssg.set_message(
                "Welcome %s user." % address_name)
            sock.sendall(hmssg.to_bytes())

            while True:
                hmssg.collect_message(sock)
                if not hmssg:
                    print("Close connection with, %s" % sock)
                    break

                logger.info("SERVER: %s" % hmssg.message_to_str())
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
            threading.Thread(target=self._client_thread,
                             args=(connection, address)).start()

        self.sock.close()

    @staticmethod
    def treaded_server(address, port):
        server = SockServer(address, port)
        thread = threading.Thread(
            target=server.run
        )
        # thread.daemon = True
        thread.start()

        return thread, server


if __name__ == "__main__":
    net_nata = sys.argv[1:]
    if len(net_nata) < 2:
        logger.info("python server_chachi.py <address> <port>")
        sys.exit(-1)

    logger.info(net_nata)
    ssrver = SockServer(net_nata[0], int(net_nata[1]))

    ssrver.run()
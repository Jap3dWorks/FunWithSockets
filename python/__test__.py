from python import client_chachi
import os
# import signal

# print(signal.SIGTERM)
import logging
os.environ["DEBUG_LEVEL"] = str(logging.DEBUG)

# client_chachi.ClientService("83.47.119.77", 8000).run()
client_chachi.ConsoleClient("127.0.0.1", 65432).run()

# Python ./python/server_chachi.py 127.0.0.1 65432
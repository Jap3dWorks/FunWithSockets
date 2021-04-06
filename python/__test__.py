from python import client_chachi
import os
# import signal

# print(signal.SIGTERM)
import logging
os.environ["DEBUG_LEVEL"] = str(logging.DEBUG)

client_chachi.ClientService("83.47.119.77", 8000).run()
# client_chachi.ClientService("127.0.0.1", 65432).run()

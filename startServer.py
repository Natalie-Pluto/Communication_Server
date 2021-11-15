import time
import sys

import server

# Start the server
serv = server.Server('127.0.0.1', 8080)
serv.run()
time.sleep(0.00001)

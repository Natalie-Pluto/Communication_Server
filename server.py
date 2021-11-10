#!/bin/python
import signal
import os
import sys
import socket
import selectors

'''
I referenced the follow website on how to establish asynchronous communication between client and server 
by using selectors module
https://www.programmerall.com/article/92511564357/
'''

#Use this variable for your loop
daemon_quit = False

# Create instance of selectors
sele = selectors.DefaultSelector()
#Do not modify or remove this handler
def quit_gracefully(signum, frame):
    global daemon_quit
    daemon_quit = True

# Process the data sent in by client
def process():
    pass


# Get data
def getData(con, addr):
    data = con.recv(1024)
    # If there's data
    if data:
        con.send(data)
        # Process the data
        process()
    else:
        # Close connection
        sele.unregister(con)
        # Close socket
        con.close()



def start_acc(sock, mask):
    # Create connection
    con, addr = sock.accept()
    # Set non-blocking
    con.setblocking(False)
    sele.register(con, selectors.EVENT_READ, getData)


def run():
    # Get the port
    port_num = sys.argv[1]
    sock_con = socket.socket()
    sock_con.setblocking(False)
    sock_con.bind(("", port_num))
    sock_con.listen(10)
    sele.register(sock_con, selectors.EVENT_READ, start_acc)
    # While the server is alive
    while not daemon_quit:
        messages = sele.select()
        for key, mask in messages:
            # Call accept function
            call_accept = key.data
            # Get accept function's address, sending in parameters
            call_accept(key.fileobj, mask)

    #Do not modify or remove this function call
    signal.signal(signal.SIGINT, quit_gracefully)


if __name__ == '__main__':
    run()



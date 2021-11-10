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


# Process "LOGIN :USERNAME :PASSWORD"
def login_pro(msg):
    pass


# Process "REGISTER :USERNAME :PASSWORD"
def register_pro(msg):
    pass


# Process "JOIN :CHANNEL"
def join_pro(msg):
    pass


# Process "CREATE :CHANNEL"
def create_pro(msg):
    pass


# Process "SAY :CHANNEL :MESSAGE"
def say_pro(msg):
    pass


# Process "RECV :USER :CHANNEL :MESSAGE"
def recv_pro(msg):
    pass


# Process "CHANNELS"
def channel_pro(msg):
    pass


# Process "RESULT JOIN :CHANNEL :CONFIRMATION"
def result_join(msg):
    pass


# Process "RESULT CREATE :CHANNEL :CONFIRMATION"
def result_create(msg):
    pass


# Porcess "RESULT (LOGIN | REGISTER) :CONFIRMATION"
def result_login(msg):
    pass


def result_register(msg):
    pass


# Process "RESULT CHANNELS [CHANNEL-NAME,. . . ]"
def result_channels(msg):
    pass


# Process the data sent in by client
def process(data):
    # Get the key word
    '''
    Assuming only "message" will contain space
    '''
    key_word = str(data).split(" ")[0].strip()


# Get data
def getData(con, addr):
    data = con.recv(1024)
    # If there's data
    if data:
        con.send(data)
        # Process the data
        process(data)
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
    sock_con.bind(("", int(port_num)))
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



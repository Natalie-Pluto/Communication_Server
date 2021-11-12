#!/bin/python
import signal
import os
import sys
import socket
import selectors
import hashlib

'''
I referenced the follow website on how to establish asynchronous communication between client and server 
by using selectors module
https://www.programmerall.com/article/92511564357/
'''

#Use this variable for your loop
daemon_quit = False

# Create instance of selectors
sele = selectors.DefaultSelector()

'''
According to the clarification on ed, database should avoid persistence. 
Therefore, I decide to use program memory rather than file.
'''
# Nested dictionary storing username, password, user's state (logged in/ logged out), joined channel
# {'username': {'password': 'salt+hashed pwd', 'state':'true/false', 'channels': 'channels'}}
db_dict = {}

# Store channels
channels = {}




#Do not modify or remove this handler
def quit_gracefully(signum, frame):
    global daemon_quit
    daemon_quit = True


# Process "LOGIN :USERNAME :PASSWORD"
def login_pro(msg):
    username = str(msg).split(" ")[1]
    # Check if this username exist
    if username in db_dict:
        # Check if the password matches
        password = str(msg).split(" ")[2].strip()
        # Get the value (salt + hashed password)
        salt = (db_dict[username]['password'])[:32]
        hashed_pwd = (db_dict[username]['password'])[32:]
        # Hash the password provided
        h_pwd = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 1000000)
        # Compare the password provided with the recorded password
        if hashed_pwd == h_pwd:
            return "RESULT LOGIN 1\n"
        else:
            return "RESULT LOGIN 0\n"


# Process "REGISTER :USERNAME :PASSWORD"
'''
I reference the follow website on how to hash the password using salt
https://nitratine.net/blog/post/how-to-hash-passwords-in-python/
'''
def register_pro(msg):
    username = str(msg).split(" ")[1]
    # Check if the username is already existed
    if username in db_dict:
        return "RESULT REGISTER 0\n"
    # Hash the password and record the key value pair
    else:
        # Get the password
        password = str(msg).split(" ")[2]
        # Generate a random salt value
        salt = os.urandom(32)
        # Hash the password
        hashed_pwd = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 1000000)
        # Store salt + password as value into the dictionary
        pwd_value = salt + hashed_pwd
        db_dict[username]['password'] = pwd_value
        return "RESULT REGISTER 1\n"


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


# Process the data sent in by client
def process(data):
    # Get the key word
    # Assuming only "message" will contain space
    key_word = str(data).split(" ")[0].strip()
    if key_word == "b'LOGIN":
        return login_pro(data)
    elif key_word == "b'REGISTER":
        return register_pro(data)
    elif key_word == "b'JOIN":
        return join_pro(data)
    elif key_word == "b'CREATE":
        return create_pro(data)
    elif key_word == "b'SAY":
        return say_pro(data)
    elif key_word == "b'RECV":
        return recv_pro(data)
    elif key_word == "b'CHANNELS":
        return channel_pro(data)
    else:
        pass


# Get data
def get_data(con, addr):
    data = con.recv(1024)
    # If there's data
    if data:
        # Process the data and send the result to client
        con.send(process(data).encode('utf-8'))

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
    sele.register(con, selectors.EVENT_READ, get_data)


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



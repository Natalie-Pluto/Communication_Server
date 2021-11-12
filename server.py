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
# Nested dictionary storing username, password, socket
# {'username': {'password': 'salt + hashed pwd', 'socket':'raddr/ null'}
db_dict = {}

# Dictionary storing channels and the users joined in each channel
# {'channel': 'username1 username2...'}
channels = {}


#Do not modify or remove this handler
def quit_gracefully(signum, frame):
    global daemon_quit
    daemon_quit = True


# Process "LOGIN :USERNAME :PASSWORD"
def login_pro(msg, raddr):
    username = msg.split(" ")[1]
    # Check if the client has logged a user
    for key, value in db_dict.items():
        for v in value:
            if v == "socket":
                if value[v] == raddr:
                    return "RESULT LOGIN 0\n"
    # Check if this username exist
    if db_dict.get(username, False):
        # Check if the user has logged in already
        if db_dict[username]['socket'] == 'na':
            # Check if the password matches
            password = msg.split(" ")[2].strip()
            # Get the value (salt + hashed password)
            salt = (db_dict[username]['password'])[:32]
            hashed_pwd = (db_dict[username]['password'])[32:]
            # Hash the password provided
            h_pwd = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 1000000)
            # Compare the password provided with the recorded password
            if hashed_pwd == h_pwd:
                db_dict[username]['socket'] = raddr
                return "RESULT LOGIN 1\n"

    return "RESULT LOGIN 0\n"


# Process "REGISTER :USERNAME :PASSWORD"
'''
I reference the follow website on how to hash the password using salt
https://nitratine.net/blog/post/how-to-hash-passwords-in-python/
'''
def register_pro(msg):
    username = msg.split(" ")[1]
    # Check if the username is already existed
    if db_dict.get(username, False):
        return "RESULT REGISTER 0\n"
    # Hash the password and record the key value pair
    else:
        # Get the password
        password = msg.split(" ")[2].strip()
        # Generate a random salt value
        salt = os.urandom(32)
        # Hash the password
        hashed_pwd = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 1000000)
        # Store salt + password as value into the dictionary
        pwd_value = salt + hashed_pwd
        db_dict[username] = {}
        db_dict[username]['password'] = pwd_value
        db_dict[username]['socket'] = 'na'
        return "RESULT REGISTER 1\n"


# Process "JOIN :CHANNEL"
def join_pro(msg, raddr):
    channel_name = msg.split(" ")[1].strip()
    # Check if this channel exist
    if channel_name in channels:
        # Check if the user is logged in & in this channel
        for key, value in db_dict.items():
            for v in value:
                if v == "socket":
                    if value[v] == raddr:
                        # User is logged in, check if he/she has joined the channel
                        if str(key) not in str(channels[channel_name]):
                            # Add user to the channel
                            users = channels[channel_name]
                            channels[channel_name] = users + " " + key
                            return "RESULT JOIN " + channel_name + " 1\n"
    return "RESULT JOIN " + channel_name + " 0\n"


# Process "CREATE :CHANNEL"
def create_pro(msg, raddr):
    channel_name = msg.split(" ")[1].strip()
    # Check if this channel exist
    if channel_name not in channels:
        # Check if the user is logged in
        for key, value in db_dict.items():
            for v in value:
                if v == "socket":
                    if value[v] == raddr:
                        # User is logged in, add this channel into database
                        channels[channel_name] = ''
                        return "RESULT CREATE " + channel_name + " 1\n"
    return "RESULT CREATE " + channel_name + " 0\n"


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
def process(data, raddr):
    # Get the key word
    # Assuming only "message" will contain space
    key_word = data.split(" ")[0].strip()
    if key_word == "LOGIN":
        return login_pro(data, raddr)
    elif key_word == "REGISTER":
        return register_pro(data)
    elif key_word == "JOIN":
        return join_pro(data, raddr)
    elif key_word == "CREATE":
        return create_pro(data, raddr)
    elif key_word == "SAY":
        return say_pro(data)
    elif key_word == "RECV":
        return recv_pro(data)
    elif key_word == "CHANNELS":
        return channel_pro(data)
    else:
        pass


# Get data
def get_data(con, mask):
    data = con.recv(1024)
    # If there's data
    if data:
        # Process the data and send the result to client
        con.send("ha")

    else:
        # Close connection
        sele.unregister(con)
        raddr = con.getpeername()
        # Log out the user
        for key, value in db_dict.items():
            for v in value:
                if v == "socket":
                    if value[v] == raddr:
                        db_dict[key][v] = 'na'
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
    sock_con.bind(('localhost', int(port_num)))
    sock_con.listen(10)
    sele.register(sock_con, selectors.EVENT_READ, start_acc)
    # While the server is alive
    while not daemon_quit:
        messages = sele.select()
        for key, mask in messages:
            # Call accept method
            call_accept = key.data
            call_accept(key.fileobj, mask)

    #Do not modify or remove this function call
    signal.signal(signal.SIGINT, quit_gracefully)


if __name__ == '__main__':
    run()



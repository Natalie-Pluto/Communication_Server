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

# Use this variable for your loop
daemon_quit = False

# Create instance of selectors
sele = selectors.DefaultSelector()

'''
According to the clarification on ed, database should avoid persistence. 
Therefore, I decide to use program memory rather than file.
'''
# Nested dictionary storing username, password, socket
# {'username': {'password': 'hashed pwd', 'socket':'con/ na'}
db_dict = {}

# Dictionary storing channels and the users joined in each channel
# {'channel': 'username1 username2...'}
channels = {}


# Do not modify or remove this handler
def quit_gracefully(signum, frame):
    global daemon_quit
    daemon_quit = True


# Process "LOGIN :USERNAME :PASSWORD"
def login_pro(msg, con):
    username = msg.split(" ")[1].strip()
    # Check if the client has logged a user
    for key, value in db_dict.items():
        for v in value:
            if v == 'socket':
                if value[v] == con:
                    return "RESULT LOGIN 0\n"
    # Check if this username exist
    if db_dict.get(username, False):
        # Check if the user has logged in already
        if db_dict[username]['socket'] == 'na':
            # Check if the password matches
            password = msg.split(" ")[2].strip()
            # Get the value (salt + hashed password)
            hashed_pwd = db_dict[username]['password']
            # Hash the password provided
            h_pwd = hashlib.md5(password.encode())
            # Compare the password provided with the recorded password
            if hashed_pwd.hexdigest() == h_pwd.hexdigest():
                db_dict[username]['socket'] = con
                return "RESULT LOGIN 1\n"

    return "RESULT LOGIN 0\n"


# Process "REGISTER :USERNAME :PASSWORD"
def register_pro(msg):
    username = msg.split(" ")[1].strip()
    # Check if the username is already existed
    if db_dict.get(username, False):
        return "RESULT REGISTER 0\n"
    # Hash the password and record the key value pair
    else:
        # Get the password
        password = msg.split(" ")[2].strip()
        # Hash the password
        hashed_pwd = hashlib.md5(password.encode())
        # Store salt + password as value into the dictionary
        db_dict[username] = {}
        db_dict[username]['password'] = hashed_pwd
        db_dict[username]['socket'] = 'na'
        return "RESULT REGISTER 1\n"


# Process "JOIN :CHANNEL"
def join_pro(msg, con):
    channel_name = msg.split(" ")[1].strip()
    # Check if this channel exist
    if channel_name in channels:
        # Check if the user is logged in & in this channel
        for key, value in db_dict.items():
            for v in value:
                if v == 'socket':
                    if value[v] == con:
                        # User is logged in, check if he/she has joined the channel
                        if str(key) not in str(channels[channel_name]):
                            # Add user to the channel
                            users = channels[channel_name]
                            channels[channel_name] = users + " " + key
                            return "RESULT JOIN " + str(channel_name) + " 1\n"
    return "RESULT JOIN " + str(channel_name) + " 0\n"


# Process "CREATE :CHANNEL"
def create_pro(msg, con):
    channel_name = msg.split(" ")[1].strip()
    # Check if this channel exist
    if channel_name not in channels:
        # Check if the user is logged in
        for key, value in db_dict.items():
            for v in value:
                if v == "socket":
                    if value[v] == con:
                        # User is logged in, add this channel into database
                        channels[channel_name] = ''
                        return "RESULT CREATE " + str(channel_name) + " 1\n"
    return "RESULT CREATE " + str(channel_name) + " 0\n"


# Process "SAY :CHANNEL :MESSAGE"
def say_pro(msg, con):
    channel_name = msg.split(" ")[1].strip()
    msg = msg.split(" ", 2)[2].strip()
    found_user = False
    # Check if this channel exist
    if channel_name in channels:
        # Check if the user is logged in
        for key, value in db_dict.items():
            for v in value:
                if v == "socket":
                    if value[v] == con:
                        found_user = True
                        # User is logged in, check if he/she has joined this channel
                        users_list = channels[channel_name]
                        if key in users_list:
                            # User has joined the channel, send the msg to all users in this channel
                            for user in str(users_list).strip().split(" "):
                                user_con = db_dict[user.strip()]['socket']
                                user_con.send(recv_pro(msg, key, channel_name).encode('utf-8'))
                        else:
                            con.send("ERROR: You Haven't Joined This Channel\n".encode('utf-8'))
        # If the user is not logged in
        if not found_user:
            con.send('ERROR: Please Log In\n'.encode('utf-8'))
    else:
        con.send('ERROR: No Such Channel\n'.encode('utf-8'))


# Process "RECV :USER :CHANNEL :MESSAGE"
def recv_pro(msg, username, channel):
    return 'RECV ' + str(username) + " " + str(channel) + " " + str(msg) + "\n"


# Process "CHANNELS"
def channel_pro():
    # return all channels stored in the dictionary
    channel_list = sorted(list(channels.keys()))
    # Format the list
    format_list = "RESULT CHANNELS "
    if len(channel_list) == 0:
        return "RESULT CHANNELS \n"
    i = 0
    while i < len(channel_list):
        if i == len(channel_list) - 1:
            format_list = format_list + channel_list[i] + "\n"
        else:
            format_list = format_list + channel_list[i] + ", "
        i += 1
    return format_list


# Process the data sent in by client
def process(data, con):
    # Get the key word
    # Assuming only "message" will contain space
    key_word = data.split(" ")[0].strip()
    if key_word == "LOGIN":
        return login_pro(data, con)
    elif key_word == "REGISTER":
        return register_pro(data)
    elif key_word == "JOIN":
        return join_pro(data, con)
    elif key_word == "CREATE":
        return create_pro(data, con)
    elif key_word == "CHANNELS":
        return channel_pro()
    else:
        pass


# Get data
def get_data(con, mask):
    try:
        data = con.recv(1024)
        # If there's data
        if data:
            # Process the data and send the result to client
            if data.decode('utf-8').strip().split(" ")[0].strip() == "SAY":
                say_pro(data.decode('utf-8').strip(), con)
            else:
                con.send(process(data.decode('utf-8').strip(), con).encode('utf-8'))
    except Exception:
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
    sock_con.bind(('localhost', int(port_num)))
    sock_con.listen(100)
    sock_con.setblocking(False)
    sele.register(sock_con, selectors.EVENT_READ, start_acc)
    # While the server is alive
    while not daemon_quit:
        messages = sele.select()
        for key, mask in messages:
            # Call accept method
            call_accept = key.data
            call_accept(key.fileobj, mask)

    # Do not modify or remove this function call
    signal.signal(signal.SIGINT, quit_gracefully)


if __name__ == '__main__':
    run()

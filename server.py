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


class Server(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

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
    def quit_gracefully(self, signum, frame):
        global daemon_quit
        daemon_quit = True

    # Process "LOGIN :USERNAME :PASSWORD"
    def login_pro(self, msg, con):
        username = msg.split(" ")[1].strip()
        # Check if the client has logged a user
        for key, value in self.db_dict.items():
            for v in value:
                if v == 'socket':
                    if value[v] == con:
                        return "RESULT LOGIN 0\n"
        # Check if this username exist
        if self.db_dict.get(username, False):
            # Check if the user has logged in already
            if self.db_dict[username]['socket'] == 'na':
                # Check if the password matches
                password = msg.split(" ")[2].strip()
                # Get the value (salt + hashed password)
                hashed_pwd = self.db_dict[username]['password']
                # Hash the password provided
                h_pwd = hashlib.md5(password.encode())
                # Compare the password provided with the recorded password
                if hashed_pwd.hexdigest() == h_pwd.hexdigest():
                    self.db_dict[username]['socket'] = con
                    return "RESULT LOGIN 1\n"

        return "RESULT LOGIN 0\n"

    # Process "REGISTER :USERNAME :PASSWORD"
    def register_pro(self, msg):
        username = msg.split(" ")[1].strip()
        # Check if the username is already existed
        if self.db_dict.get(username, False):
            return "RESULT REGISTER 0\n"
        # Hash the password and record the key value pair
        else:
            # Get the password
            password = msg.split(" ")[2].strip()
            # Hash the password
            hashed_pwd = hashlib.md5(password.encode())
            # Store salt + password as value into the dictionary
            self.db_dict[username] = {}
            self.db_dict[username]['password'] = hashed_pwd
            self.db_dict[username]['socket'] = 'na'
            return "RESULT REGISTER 1\n"

    # Process "JOIN :CHANNEL"
    def join_pro(self, msg, con):
        channel_name = msg.split(" ")[1].strip()
        # Check if this channel exist
        if channel_name in self.channels:
            # Check if the user is logged in & in this channel
            for key, value in self.db_dict.items():
                for v in value:
                    if v == 'socket':
                        if value[v] == con:
                            # User is logged in, check if he/she has joined the channel
                            if str(key) not in str(self.channels[channel_name]):
                                # Add user to the channel
                                users = self.channels[channel_name]
                                self.channels[channel_name] = users + " " + key
                                return "RESULT JOIN " + str(channel_name) + " 1\n"
        return "RESULT JOIN " + str(channel_name) + " 0\n"

    # Process "CREATE :CHANNEL"
    def create_pro(self, msg, con):
        channel_name = msg.split(" ")[1].strip()
        # Check if this channel exist
        if channel_name not in self.channels:
            # Check if the user is logged in
            for key, value in self.db_dict.items():
                for v in value:
                    if v == "socket":
                        if value[v] == con:
                            # User is logged in, add this channel into database
                            self.channels[channel_name] = ''
                            return "RESULT CREATE " + str(channel_name) + " 1\n"
        return "RESULT CREATE " + str(channel_name) + " 0\n"

    # Process "SAY :CHANNEL :MESSAGE"
    def say_pro(self, msg, con):
        channel_name = msg.split(" ")[1].strip()
        msg = msg.split(" ", 2)[2].strip()
        found_user = False
        # Check if this channel exist
        if channel_name in self.channels:
            # Check if the user is logged in
            for key, value in self.db_dict.items():
                for v in value:
                    if v == "socket":
                        if value[v] == con:
                            found_user = True
                            # User is logged in, check if he/she has joined this channel
                            users_list = self.channels[channel_name]
                            if key in users_list:
                                # User has joined the channel, send the msg to all users in this channel
                                for user in str(users_list).strip().split(" "):
                                    user_con = self.db_dict[user.strip()]['socket']
                                    user_con.send(self.recv_pro(msg, key, channel_name).encode('utf-8'))
                            else:
                                con.send("ERROR: You Haven't Joined This Channel\n".encode('utf-8'))
            # If the user is not logged in
            if not found_user:
                con.send('ERROR: Please Log In\n'.encode('utf-8'))
        else:
            con.send('ERROR: No Such Channel\n'.encode('utf-8'))

    # Process "RECV :USER :CHANNEL :MESSAGE"
    def recv_pro(self, msg, username, channel):
        return 'RECV ' + str(username) + " " + str(channel) + " " + str(msg) + "\n"

    # Process "CHANNELS"
    def channel_pro(self):
        # return all channels stored in the dictionary
        channel_list = sorted(list(self.channels.keys()))
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
    def process(self, data, con):
        # Get the key word
        # Assuming only "message" will contain space
        key_word = data.split(" ")[0].strip()
        if key_word == "LOGIN":
            return self.login_pro(data, con)
        elif key_word == "REGISTER":
            return self.register_pro(data)
        elif key_word == "JOIN":
            return self.join_pro(data, con)
        elif key_word == "CREATE":
            return self.create_pro(data, con)
        elif key_word == "CHANNELS":
            return self.channel_pro()
        else:
            pass

    # Get data
    def get_data(self, con, mask):
        try:
            data = con.recv(1024)
            # If there's data
            if data:
                # Process the data and send the result to client
                if data.decode('utf-8').strip().split(" ")[0].strip() == "SAY":
                    self.say_pro(data.decode('utf-8').strip(), con)
                else:
                    con.send(self.process(data.decode('utf-8').strip(), con).encode('utf-8'))
        except Exception:
            # Close connection
            self.sele.unregister(con)
            # Close socket
            con.close()

    def start_acc(self, sock, mask):
        # Create connection
        con, addr = sock.accept()
        # Set non-blocking
        con.setblocking(False)
        self.sele.register(con, selectors.EVENT_READ, self.get_data)

    def run(self):
        sock_con = socket.socket()
        sock_con.bind((self.host, self.port))
        sock_con.listen(100)
        sock_con.setblocking(False)
        self.sele.register(sock_con, selectors.EVENT_READ, self.start_acc)
        # While the server is alive
        while not self.daemon_quit:
            messages = self.sele.select()
            for key, mask in messages:
                # Call accept method
                call_accept = key.data
                call_accept(key.fileobj, mask)

        # Do not modify or remove this function call
        signal.signal(signal.SIGINT, self.quit_gracefully)


if __name__ == '__main__':
    port_num = sys.argv[1]
    host = ""
    server = Server(host, int(port_num))
    server.run()

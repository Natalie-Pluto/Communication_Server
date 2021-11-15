import json
import os
import unittest
import socket

# Unittests for server.py
# Referenced the follow website:
# https://www.sealights.io/agile-testing/test-metrics/python-code-coverage/
# https://www.devdungeon.com/content/unit-testing-tcp-server-client-python
import server


class ServerTest(unittest.TestCase):
    result_list = []

    # Test successful register
    def test_register(self):
        data_list_exp = ['RESULT REGISTER 1\n']
        data_list = []
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect(('localhost', 8080))
        msg = [b'REGISTER user233 hunter2']
        serv = server.Server('127.0.0.1', 8080)
        for m in msg:
            serv.process(m.decode('utf-8'), sk)
            sk.send(m)
            data = sk.recv(1024)
            data_list.append(data.decode('utf-8'))
        sk.close()
        # Check the result
        if self.assertEqual(data_list_exp, data_list, "False"):
            self.result_list.append({"test_register" : "Failed"})
        else:
            self.result_list.append({"test_register" : "Passed"})

    # Test duplicate username
    def test_register_fail1(self):
        data_list_exp = ['RESULT REGISTER 0\n']
        data_list = []
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect(('localhost', 8080))
        msg = [b'REGISTER user233 hunter2']
        serv = server.Server('127.0.0.1', 8080)
        for m in msg:
            serv.process(m.decode('utf-8'), sk)
            sk.send(m)
            data = sk.recv(1024)
            data_list.append(data.decode('utf-8'))
        sk.close()
        # Check the result
        if self.assertEqual(data_list_exp, data_list, "False"):
            self.result_list.append({"test_register_fail1" : "Failed"})
        else:
            self.result_list.append({"test_register_fail1r" : "Passed"})
        jsonString = json.dumps(self.result_list, indent=1)
        jsonFile = open("test_result.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()
        os.system("ps -ef | grep startServer | grep -v grep | awk '{print $2}' | xargs kill")

    # Test successful login
    def test_login1(self):
        data_list_exp = ['RESULT REGISTER 1\n', 'RESULT LOGIN 1\n']
        data_list = []
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect(('localhost', 8080))
        msg = [b'REGISTER user20 hunter2', b'LOGIN user20 hunter2']
        serv = server.Server('127.0.0.1', 8080)
        for m in msg:
            serv.process(m.decode('utf-8'), sk)
            sk.send(m)
            data = sk.recv(1024)
            data_list.append(data.decode('utf-8'))
        sk.close()
        # Check the result
        if self.assertEqual(data_list_exp, data_list, "False"):
            self.result_list.append({"test_login1" : "Failed"})
        else:
            self.result_list.append({"test_login1" : "Passed"})

    # User not exist
    def test_login_fail(self):
        data_list_exp = ['RESULT REGISTER 1\n', 'RESULT LOGIN 0\n']
        data_list = []
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect(('localhost', 8080))
        msg = [b'REGISTER user30 hunter2', b'LOGIN user2 hunter2']
        serv = server.Server('127.0.0.1', 8080)
        for m in msg:
            serv.process(m.decode('utf-8'), sk)
            sk.send(m)
            data = sk.recv(1024)
            data_list.append(data.decode('utf-8'))
        sk.close()
        # Check the result
        if self.assertEqual(data_list_exp, data_list, "False"):
            self.result_list.append({"test_login_fail" : "Failed"})
        else:
            self.result_list.append({"test_login_fail" : "Passed"})

    # Same client can't login twice
    def test_login_fail2(self):
        data_list_exp = ['RESULT REGISTER 1\n', 'RESULT LOGIN 1\n', 'RESULT LOGIN 0\n']
        data_list = []
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect(('localhost', 8080))
        msg = [b'REGISTER user22 hunter2', b'LOGIN user30 hunter2', b'LOGIN user22 hunter2']
        serv = server.Server('127.0.0.1', 8080)
        for m in msg:
            serv.process(m.decode('utf-8'), sk)
            sk.send(m)
            data = sk.recv(1024)
            data_list.append(data.decode('utf-8'))
        sk.close()
        # Check the result
        if self.assertEqual(data_list_exp, data_list, "False"):
            self.result_list.append({"test_login_fail2" : "Failed"})
        else:
            self.result_list.append({"test_login_fail2" : "Passed"})

    # Wrong password
    def test_login_fail3(self):
        data_list_exp = ['RESULT REGISTER 1\n', 'RESULT LOGIN 0\n']
        data_list = []
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect(('localhost', 8080))
        msg = [b'REGISTER user2 hunter2', b'LOGIN user2 lol']
        serv = server.Server('127.0.0.1', 8080)
        for m in msg:
            serv.process(m.decode('utf-8'), sk)
            sk.send(m)
            data = sk.recv(1024)
            data_list.append(data.decode('utf-8'))
        sk.close()
        # Check the result
        if self.assertEqual(data_list_exp, data_list, "False"):
            self.result_list.append({"test_login_fail3" : "Failed"})
        else:
            self.result_list.append({"test_login_fail3" : "Passed"})

    # Successful create channel
    def test_create(self):
        data_list_exp = ['RESULT REGISTER 1\n', 'RESULT LOGIN 1\n', 'RESULT CREATE Disney 1\n']
        data_list = []
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect(('localhost', 8080))
        msg = [b'REGISTER user21 hunter2', b'LOGIN user21 hunter2', b'CREATE Disney']
        serv = server.Server('127.0.0.1', 8080)
        for m in msg:
            serv.process(m.decode('utf-8'), sk)
            sk.send(m)
            data = sk.recv(1024)
            data_list.append(data.decode('utf-8'))
        sk.close()
        # Check the result
        if self.assertEqual(data_list_exp, data_list, "False"):
            self.result_list.append({"test_create" : "Failed"})
        else:
            self.result_list.append({"test_create" : "Passed"})


    # Can't create duplicate channel
    def test_create_fail(self):
        data_list_exp = ['RESULT REGISTER 1\n', 'RESULT LOGIN 1\n', 'RESULT CREATE Disney 0\n']
        data_list = []
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect(('localhost', 8080))
        msg = [b'REGISTER user32 hunter2', b'LOGIN user32 hunter2', b'CREATE Disney']
        serv = server.Server('127.0.0.1', 8080)
        for m in msg:
            serv.process(m.decode('utf-8'), sk)
            sk.send(m)
            data = sk.recv(1024)
            data_list.append(data.decode('utf-8'))
        sk.close()
        # Check the result
        if self.assertEqual(data_list_exp, data_list, "False"):
            self.result_list.append({"test_create_fail" : "Failed"})
        else:
            self.result_list.append({"test_create_fail" : "Passed"})

    # Successful join channel
    def test_join(self):
        data_list_exp = ['RESULT REGISTER 1\n', 'RESULT LOGIN 1\n', 'RESULT JOIN Disney 1\n']
        data_list = []
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect(('localhost', 8080))
        msg = [b'REGISTER user33 hunter2', b'LOGIN user33 hunter2', b'JOIN Disney']
        serv = server.Server('127.0.0.1', 8080)
        for m in msg:
            serv.process(m.decode('utf-8'), sk)
            sk.send(m)
            data = sk.recv(1024)
            data_list.append(data.decode('utf-8'))
        sk.close()
        # Check the result
        if self.assertEqual(data_list_exp, data_list, "False"):
            self.result_list.append({"test_join" : "Failed"})
        else:
            self.result_list.append({"test_join" : "Passed"})

    # Failed join channel
    def test_join_fail(self):
        data_list_exp = ['RESULT REGISTER 1\n', 'RESULT LOGIN 1\n', 'RESULT JOIN Universal 0\n']
        data_list = []
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect(('localhost', 8080))
        msg = [b'REGISTER user34 hunter2', b'LOGIN user34 hunter2', b'JOIN Universal']
        serv = server.Server('127.0.0.1', 8080)
        for m in msg:
            serv.process(m.decode('utf-8'), sk)
            sk.send(m)
            data = sk.recv(1024)
            data_list.append(data.decode('utf-8'))
        sk.close()
        # Check the result
        if self.assertEqual(data_list_exp, data_list, "False"):
            self.result_list.append({"test_join_fail" : "Failed"})
        else:
            self.result_list.append({"test_join_fail" : "Passed"})


    # Say auccessul
    def test_say(self):
        data_list_exp = ['RESULT REGISTER 1\n', 'RESULT LOGIN 1\n', 'RESULT JOIN Universal 0\n']
        data_list = []
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect(('localhost', 8080))
        msg = [b'REGISTER user34 hunter2', b'LOGIN user34 hunter2', b'JOIN Universal']
        serv = server.Server('127.0.0.1', 8080)
        for m in msg:
            serv.process(m.decode('utf-8'), sk)
            sk.send(m)
            data = sk.recv(1024)
            data_list.append(data.decode('utf-8'))
        sk.close()
        # Check the result
        if self.assertEqual(data_list_exp, data_list, "False"):
            self.result_list.append({"test_join_fail" : "Failed"})
        else:
            self.result_list.append({"test_join_fail" : "Passed"})




if __name__ == '__main__':
    unittest.main()


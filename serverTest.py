import json
import os
import unittest
import socket
import server
# Unittests for server.py
# Referenced the follow website:
# https://www.sealights.io/agile-testing/test-metrics/python-code-coverage/
# https://www.devdungeon.com/content/unit-testing-tcp-server-client-python
'''
Test report (Json File) will be generated automatically after all the tests
have been ran. It will be shown in the same directory
Please run the test and generate the coverage report using commands addressed in readme
'''


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
        try:
            self.assertEqual(data_list_exp, data_list, "False")
            self.result_list.append({"test_register" : "Passed"})
        except:
            self.result_list.append({"test_register" : "Failed"})
            self.assertEqual(data_list_exp, data_list, "False")

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
        try:
            self.assertEqual(data_list_exp, data_list, "False")
            self.result_list.append({"test_register_fail1" : "Passed"})
        except:
            self.result_list.append({"test_register_fail1" : "Failed"})
            self.assertEqual(data_list_exp, data_list, "False")

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
        try:
            self.assertEqual(data_list_exp, data_list, "False")
            self.result_list.append({"test_login1" : "Passed"})
        except:
            self.result_list.append({"test_login1" : "Failed"})
            self.assertEqual(data_list_exp, data_list, "False")

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
        try:
            self.assertEqual(data_list_exp, data_list, "False")
            self.result_list.append({"test_login_fail" : "Passed"})
        except:
            self.result_list.append({"test_login_fail" : "Failed"})
            self.assertEqual(data_list_exp, data_list, "False")

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
        try:
            self.assertEqual(data_list_exp, data_list, "False")
            self.result_list.append({"test_login_fail2" : "Passed"})
        except:
            self.result_list.append({"test_login_fail2" : "Failed"})
            self.assertEqual(data_list_exp, data_list, "False")

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
        try:
            self.assertEqual(data_list_exp, data_list, "False")
            self.result_list.append({"test_login_fail3" : "Passed"})
        except:
            self.result_list.append({"test_login_fail3" : "Failed"})
            self.assertEqual(data_list_exp, data_list, "False")

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
        try:
            self.assertEqual(data_list_exp, data_list, "False")
            self.result_list.append({"test_create" : "Passed"})
        except:
            self.result_list.append({"test_create" : "Failed"})
            self.assertEqual(data_list_exp, data_list, "False")


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
        try:
            self.assertEqual(data_list_exp, data_list, "False")
            self.result_list.append({"test_create_fail" : "Passed"})
        except:
            self.result_list.append({"test_create_fail" : "Failed"})
            self.assertEqual(data_list_exp, data_list, "False")

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
        try:
            self.assertEqual(data_list_exp, data_list, "False")
            self.result_list.append({"test_join" : "Passed"})
        except:
            self.result_list.append({"test_join" : "Failed"})
            self.assertEqual(data_list_exp, data_list, "False")

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
        try:
            self.assertEqual(data_list_exp, data_list, "False")
            self.result_list.append({"test_join_fail" : "Passed"})
        except:
            self.result_list.append({"test_join_fail" : "Failed"})
            self.assertEqual(data_list_exp, data_list, "False")


    # Say auccessul
    def test_say(self):
        data_list_exp = ['RESULT REGISTER 1\n', 'RESULT LOGIN 1\n', 'RESULT JOIN Disney 1\n', 'RECV user35 Disney Hello from Mickey\n']
        data_list = []
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect(('localhost', 8080))
        msg = [b'REGISTER user35 hunter2', b'LOGIN user35 hunter2', b'JOIN Disney', b'SAY Disney Hello from Mickey']
        serv = server.Server('127.0.0.1', 8080)
        for m in msg:
            sk.send(m)
            data = sk.recv(1024)
            data_list.append(data.decode('utf-8'))
        serv.say_pro(b'SAY Disney Hello from Mickey'.decode('utf-8'), sk)
        sk.close()
        # Check the result
        try:
            self.assertEqual(data_list_exp, data_list, "False")
            self.result_list.append({"test_say" : "Passed"})
        except:
            self.result_list.append({"test_say" : "Failed"})
            self.assertEqual(data_list_exp, data_list, "False")

    # Not exist channel
    def test_say_fail(self):
        data_list_exp = ['RESULT REGISTER 1\n', 'RESULT LOGIN 1\n', 'RESULT JOIN Disney 1\n', 'ERROR: No Such Channel\n']
        data_list = []
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect(('localhost', 8080))
        msg = [b'REGISTER user38 hunter2', b'LOGIN user38 hunter2', b'JOIN Disney', b'SAY Disneyy Hello from Mickey']
        serv = server.Server('127.0.0.1', 8080)
        for m in msg:
            sk.send(m)
            data = sk.recv(1024)
            data_list.append(data.decode('utf-8'))
            if m.decode('utf-8').split(" ")[0] != 'SAY':
                serv.process(m.decode('utf-8'), sk)
            else:
                serv.say_pro(b'SAY Disneyy Hello from Mickey'.decode('utf-8'), sk)
        sk.close()
        # Check the result
        try:
            self.assertEqual(data_list_exp, data_list, "False")
            self.result_list.append({"test_say_fail" : "Passed"})
        except:
            self.result_list.append({"test_say_fail" : "Failed"})
            self.assertEqual(data_list_exp, data_list, "False")

    # Not exist channel
    def test_say_fail2(self):
        data_list_exp = ['RESULT REGISTER 1\n', 'RESULT LOGIN 1\n', 'RESULT CREATE Hogwarts 1\n', 'RESULT JOIN Disney 1\n', "ERROR: You Haven't Joined This Channel\n"]
        data_list = []
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect(('localhost', 8080))
        msg = [b'REGISTER user40 hunter2', b'LOGIN user40 hunter2',  b'CREATE Hogwarts', b'JOIN Disney', b'SAY Hogwarts Hello from Mickey']
        serv = server.Server('127.0.0.1', 8080)
        for m in msg:
            sk.send(m)
            data = sk.recv(1024)
            data_list.append(data.decode('utf-8'))
            if m.decode('utf-8').split(" ")[0] != 'SAY':
                serv.process(m.decode('utf-8'), sk)
            else:
                serv.say_pro(b'SAY Hogwarts Hello from Mickey'.decode('utf-8'), sk)
        sk.close()
        # Check the result
        try:
            self.assertEqual(data_list_exp, data_list, "False")
            self.result_list.append({"test_say_fail2" : "Passed"})
        except:
            self.result_list.append({"test_say_fail2" : "Failed"})
            self.assertEqual(data_list_exp, data_list, "False")

    # Test list all channels
    def test_channel(self):
        data_list_exp = ['RESULT REGISTER 1\n', 'RESULT LOGIN 1\n', 'RESULT CREATE Hi 1\n', 'RESULT CHANNELS Hi\n']
        data_list = []
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect(('localhost', 8080))
        msg = [b'REGISTER user37 hunter2', b'LOGIN user37 hunter2', b'CREATE Hi', b'CHANNELS']
        serv = server.Server('127.0.0.1', 8080)
        for m in msg:
            serv.process(m.decode('utf-8'), sk)
            sk.send(m)
            data = sk.recv(1024)
            data_list.append(data.decode('utf-8'))
        sk.close()
        # Check the result
        try:
            self.assertEqual(data_list_exp, data_list, "False")
            self.result_list.append({"test_channel": "Passed"})
        except:
            self.result_list.append({"test_channel": "Failed"})
            self.assertEqual(data_list_exp, data_list, "False")







    # Kill the server, generate test report
    def test_zzz(self):
        jsonString = json.dumps(self.result_list, indent=1)
        jsonFile = open("test_result.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()
        os.system("ps -ef | grep startServer | grep -v grep | awk '{print $2}' | xargs kill")


if __name__ == '__main__':
    unittest.main()




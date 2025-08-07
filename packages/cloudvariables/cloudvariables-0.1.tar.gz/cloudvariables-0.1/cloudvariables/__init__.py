import socket as sk
import os
import json
import random
from coder import *
import sys
sys.set_int_max_str_digits(2000000000)

class Net:
    def __init__(self):
        self.__port = 10101
        self.__server = "127.0.0.1"
        self.__s = None
        self.__token = None
        self.__password = None
        self.__codec = "UTF-8"

    def __send(self, value, ra = False):
        self.__s.send(str(len(value.encode(self.__codec))).encode(self.__codec))
        self.__s.recv(16)
        self.__s.send(str(value).encode(self.__codec))
        if not ra:
            self.__s.recv(16)

    def __recv(self, buffer = 64, er = True):
        rs = self.__s.recv(buffer).decode(self.__codec)
        self.__s.send("1".encode(self.__codec))
        v = self.__s.recv(int(rs)).decode(self.__codec)
        if er:
            self.__s.send("1".encode(self.__codec))
        return v

    def set_port(self, newport):
        if str(newport).isdigit():
            if 1024 < int(newport) < 2**12:
                self.__port = int(newport)
                return "1"
            else:
                return "3"
        else:
            return "2"

    def set_server(self, new_server, ip_type):
        if ip_type == 1:
            splited_set_server = str(new_server).split(".")
            if len(splited_set_server) == 4:
                are_digital = False
                for i in splited_set_server:
                    j = int(i)
                    if str(j).isdigit() and j <= 255:
                        are_digital = True
                if are_digital:
                    self.__server = new_server
        else:
            self.__server = new_server

    def start(self):
        self.__s = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        self.__s.connect((self.__server, self.__port))
        self.__s.send("1".encode("UTF-8"))
        self.__codec = self.__s.recv(100).decode("UTF-8")
        self.__s.send(self.__codec.encode("UTF-8"))

    def connect(self, token, password):
        self.__token = str(token)
        self.__password = str(password)

    def create(self, password):
        mode = "create"
        self.__send(mode)
        self.__send(password, ra=True)

        return self.__recv()

    def del_var(self, variable):
        mode = "delete variable"
        self.__send(mode)
        self.__send(self.__token)
        self.__send(self.__password, ra=True)
        r = self.__s.recv(12).decode(self.__codec)
        if r == "1":
            self.__send(variable)
        elif r == "ER1":
            print("Wrong token")
        elif r == "ER2":
            print("Wrong password")

    def del_proj(self, passw):
        mode = "delete project"
        self.__send(mode)
        self.__send(self.__token)
        self.__send(self.__password, ra=True)
        r = self.__s.recv(12).decode(self.__codec)
        if r == "1":
            self.__send(passw)
        elif r == "ER1":
            print("Wrong token")
        elif r == "ER2":
            print("Wrong password")

    def set(self, variable, value):
        mode = "write"
        self.__send(mode)
        self.__send(self.__token)
        self.__send(self.__password, ra=True)
        r = self.__s.recv(12).decode(self.__codec)
        if r == "1":
            self.__send(variable)
            self.__send(value)
        elif r == "ER1":
            print("Wrong token")
        elif r == "ER2":
            print("Wrong password")

    def get(self, variable):
        mode = "read"
        self.__send(mode)
        self.__send(self.__token)
        self.__send(self.__password, ra=True)
        r = self.__s.recv(12).decode(self.__codec)
        if r == "1":
            self.__send(variable, ra=True)
            value = self.__recv()
            return value
        elif r == "ER1":
            print("Wrong token")
            return "ERROR"
        elif r == "ER2":
            print("Wrong password")
            return "ERROR"

class Server:
    def __init__(self, port = 10101, server = 0, codec = "UTF-8", limit = 0):
        if str(port).isdigit():
            self.__port = int(port)
        else:
            self.__port = 10101
        self.__server = ""
        self.__s = None
        self.codec = codec
        self.__limit = None
        inf = float("inf")
        if str(limit).isdigit():
            if int(limit) == 0:
                self.__limit = inf
            elif int(limit) > 0:
                self.__limit = int(limit)
        else:
            self.__limit = inf
        match str(server):
            case "0":
                self.__server = ""
            case "1":
                self.__server = sk.gethostbyname(sk.gethostname())
            case "2":
                self.__server = "127.0.0.1"
            case _:
                self.__server = str(server)

    def get_base(self, c):
        if os.path.exists("b.bcv"):
            return json.loads(dcode("b.bcv", c))
        else:
            return {}

    def backup(self, c, b):
        ncode("b.bcv", c, json.dumps(str(b).replace("'", "\"")))

    def start(self):
        s = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        s.bind((self.__server, self.__port))
        s.listen()
        return s

    def gen_token(self, g):
        symbols = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "a", "b", "c", "d", "e", "f", "g", "h", "i", "g",
                   "k", "l",
                   "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D", "E", "F",
                   "G", "H",
                   "I", "G", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        while True:
            new_token = ""
            for i in range(20):
                new_token += random.choice(symbols)
            if new_token not in g:
                return new_token

    def get_port(self):
        return self.__port
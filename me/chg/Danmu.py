import multiprocessing
import time
from datetime import datetime
import socket
import struct
import re

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('openbarrage.douyutv.com', 8601))


def main(roomid):
    login(s, roomid)
    while True:
        d = s.recv(1024)
        if d:
            package = DataPackage(690)
            package.form(d)
            handle_msg(s, package)
        else:
            break


def login(s, roomid):
    data = DataPackage(689, type='loginreq', roomid=roomid).pack()
    s.send(data)
    data = DataPackage(689, type='joingroup', rid=roomid, gid='-9999').pack()
    s.send(data)


def handle_msg(s, data_package):
    print('receive:' + data_package.__str__())
    typ = data_package.type
    if typ == 'chatmsg':
        print("[%s]%s"%(data_package.nn, data_package.txt))


class DataPackage(object):

    tag = ('type','roomid','tick','rid','gid')

    attr = re.compile(rb'(\w+)@=(.*?)/')

    def form(self, data):
        attrs = DataPackage.attr.findall(data)
        for a in attrs:
            self.dict[a[0].decode('utf-8')] = a[1].decode('utf-8')

    def __init__(self, code, **kw):
        self.dict = {}
        self.reqcode = code
        self.dict.update(kw)

    def __setattr__(self, key, value):
        if key in DataPackage.tag:
            self.dict[key] = str(value)
        else:
            super(DataPackage, self).__setattr__(key, value)

    def __getattr__(self, item):
        if item in self.dict:
            return self.dict[item]

    def pack(self):
        data = ''
        for k, v in self.dict.items():
            data = data + k + '@=' + v + '/'
        data = data.encode('utf-8') + b'\0'
        data_length = len(data) + 8
        header = struct.pack('<l', data_length) + struct.pack('<l', data_length) + struct.pack('<I', self.reqcode)
        #print('send:' + self.__str__())
        return header + data

    def __str__(self):
        s = ''
        for k, v in self.dict.items():
            s = s + k + '=' + v + ';'
        return s


def keep_alive():
    data = DataPackage(689, type='mrkl').pack()
    s.send(data)
    time.sleep(40)


if __name__ == '__main__':
    p1 = multiprocessing.Process(target=main, args=('30191',))
    p2 = multiprocessing.Process(target=keep_alive)
    p1.start()
    p2.start()


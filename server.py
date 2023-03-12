""" 服务器 """
import socket
import threading

from constants import *

__version__ = '0.0.1'
__author__ = '小康2022<2951256653@qq.com>'


class Server:
    """ 服务器 """

    server = socket.socket()
    server.bind(('', PORT))
    server.listen(128)

    @classmethod
    def accept(cls) -> None:
        """ 等待 """
        print('SERVER LAUNCH')
        while True:
            try:
                client, retaddress = cls.server.accept()
                threading.Thread(
                    target=Client, args=(client, retaddress), daemon=True).start()
            except Exception as error:
                print(error.__repr__())


class Client:
    """ 客户端 """

    def __init__(self, client: socket.socket, retaddress: tuple[str, int]) -> None:
        self.client = client
        self.address = retaddress[0]
        self.port = retaddress[1]
        self.run()

    def verify(self) -> bool:
        """ 判断 """
        try:
            return self.recv()['code'] == 'CLIENT'
        except:
            return False

    def close(self) -> None:
        """ 断开 """
        self.client.close()
        print('LOST: %s' % self.address)

    def send(self, **kw) -> None:
        """ 发送 """
        return self.client.send(kw.__repr__().encode())

    def recv(self) -> dict:
        """ 接受 """
        return eval(self.client.recv(4096).decode())

    def run(self) -> None:
        """ 执行 """
        if not self.verify():
            return self.client.close()
        print('CONNECT: %s' % self.address)
        while True:
            data = self.recv()
            if data['code'] == 'QUIT':
                return self.close()


if __name__ == '__main__':
    Server.accept()

""" 服务器 """

import socket
import threading
import time

import mail
from constants import *

__version__ = '0.0.2'
__author__ = '小康2022<2951256653@qq.com>'

logfile = open('Logs.log', 'a', encoding='utf-8')


def output(mode: str, msg: str) -> None:
    """ 终端信息输出 """
    _time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print('\r\033[36m%s\033[0m [%s] \033[30m>\033[0m %s' % (_time, mode, msg))
    print('%s [%s] > %s' % (_time, mode[5:-4], msg), file=logfile, flush=True)


output(INFO, '%s Server: v%s' % (NAME, __version__))


class Server:
    """ 服务器 """

    output(INFO, '创建服务端套接字')
    server = socket.socket()
    output(INFO, '绑定端口: %s' % PORT)
    server.bind(('', PORT))
    output(INFO, '设置服务端监听最大数量: %d' % MAXIMUM)
    server.listen(MAXIMUM)

    @classmethod
    def accept(cls) -> None:
        """ 等待 """
        while True:
            try:
                client, retaddress = cls.server.accept()
                threading.Thread(
                    target=Client, args=(client, retaddress), daemon=True).start()
            except Exception as error:
                output(ERROR, error.__repr__())

    @classmethod
    def input(cls, count: int = 0) -> None:
        """ 终端命令输入 """
        while True:
            count += 1
            match input('\033[32mIn [%d]:\033[0m ' % count):
                case 'quit' | 'exit' | 'shutdown':
                    exit()
                case _:
                    print('\033[35mOut[%d]:\033[0m Unknow command' % count)


class User:
    """ 用户 """

    def __init__(self) -> None:
        pass


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
            return self.recv()['op'] == 'CLIENT'
        except:
            return False

    def close(self) -> None:
        """ 断开 """
        self.client.close()
        output(INFO, 'LOST: %s' % self.address)

    def send(self, **kw) -> None:
        """ 发送 """
        return self.client.send(kw.__repr__().encode())

    def recv(self) -> dict:
        """ 接受 """
        return eval(self.client.recv(PACK_SIZE).decode())

    def run(self) -> None:
        """ 执行 """
        if not self.verify():
            return self.client.close()
        output(INFO, 'CONNECT: %s' % self.address)
        while True:
            data = self.recv()
            if data['op'] == 'QUIT':
                return self.close()
            if data['op'] == 'CODE':
                code = mail.code()
                try:
                    output(INFO, '发送验证码到 %s' % data['mail'])
                    mail.send(data['mail'], code)
                except:
                    output(WARN, '无法发送验证码到 %s！' % data['mail'])


if __name__ == '__main__':
    output(INFO, '启动客户端监听功能')
    threading.Thread(target=Server.accept, daemon=True).start()
    output(INFO, '启动服务端命令功能')
    Server.input()

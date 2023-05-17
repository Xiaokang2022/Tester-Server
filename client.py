""" 客户端功能 """
import socket

from log import logger
from mail import Email
from randcode import Code
from timer import Countdown
from user import User


def Error() -> None:
    raise TimeoutError('TimeoutError')


class Client:
    """ 客户端 """

    pack_size = 4096
    connection = []  # type: list[Client]

    def __init__(self, client: socket.socket, retaddress: tuple[str, int]) -> None:
        self.client = client
        # self.client.settimeout(3600)
        self.address, self.port = retaddress
        Client.connection.append(self)
        self.verify()
        self.process()

    def verify(self) -> None:
        """ 身份验证 """
        try:
            cd = Countdown(15, Error)
            if self.recv()['op'] == 'CLIENT':
                logger.info('客户端连接 (%s : %d)' % (self.address, self.port))
                return cd.destroy()
            self.close()
        except Exception as error:
            logger.warning('身份验证失败, %s' % error)
            self.close()

    def send(self, **kw) -> None:
        """ 发送 """
        try:
            self.client.send(kw.__repr__().encode())
        except Exception as error:
            logger.warning('数据发送失败, %s' % error)

    def recv(self) -> dict:
        """ 接受 """
        try:
            return eval(self.client.recv(self.pack_size).decode())
        except Exception as error:
            logger.warning('数据接收失败, %s' % error)
            return {'op': 'QUIT'}

    def close(self) -> None:
        """ 断开连接 """
        Client.connection.remove(self)
        self.client.close()
        logger.info('客户端断开 (%s : %s)' % (self.address, self.port))

    def process(self) -> None:
        """ 逻辑处理 """
        while self in Client.connection:
            match (msg := self.recv())['op']:
                case 'REFRESH':
                    continue
                case 'QUIT':
                    return self.close()
                case 'CODE':
                    Email(msg['mail'], Email.build_codemsg(
                        msg['mail'], Code(msg['mail']).value), 'Questioner服务器验证码').send()
                case 'REGISTER':
                    if User.data.get(msg['mail'], None):  # 账号已存在
                        self.send(op='REGISTER', state='REPEAT')
                    elif msg['code'] in Code.codes and msg['mail'] == Code.codes[msg['code']].mail:
                        Code.codes[msg['code']].cancel()
                        logger.info('%s 注册成功' % msg['mail'])
                        User.new(msg['name'], msg['mail'], msg['psd'])
                        self.send(op='REGISTER', state='OK')
                        Email(msg['mail'], Email.build_regmsg(
                            msg['name']), 'Questioner 账号注册成功').send()
                    else:  # 验证码无效
                        self.send(op='REGISTER', state='CODE_ERROR')
                case 'LOGIN':
                    if User.data.get(msg['mail'], None):
                        if msg['mode'] == 'PASSWORD':
                            if msg['psd'] == User.data[msg['mail']]['psd']:
                                logger.info('%s 登录成功' % msg['mail'])
                                self.send(op='LOGIN', state='OK', data=None)
                            else:  # 密码错误
                                self.send(op='LOGIN', state='ERROR')
                        else:
                            if msg['code'] in Code.codes and msg['mail'] == Code.codes[msg['code']].mail:
                                Code.codes[msg['code']].cancel()
                                logger.info('%s 登录成功' % msg['mail'])
                                self.send(op='LOGIN', state='OK', data=None)
                            else:  # 验证码错误
                                self.send(op='LOGIN', state='CODE_ERROR')
                    else:  # 账号不存在
                        self.send(op='LOGIN', state='ERROR')


if __name__ == '__main__':
    pass

""" 服务器 """

import json
import os
import random
import smtplib
import socket
import threading
import time
from email.mime.text import MIMEText

from constants import *

__version__ = '0.0.3'
__author__ = '小康2022<2951256653@qq.com>'

logfile = open('Logs.log', 'a', encoding='utf-8')

users = {}  # type: dict[str, User]  # 已注册用户
_users = {}  # type: dict[str, _User]  # 临时用户（待注册）


def output(mode: str, msg: str) -> None:
    """ 终端信息输出 """
    _time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print('\r\033[36m%s\033[0m [%s] \033[30m>\033[0m %s' % (_time, mode, msg))
    print('%s [%s] > %s' % (_time, mode[5:-4], msg), file=logfile, flush=True)


class CountDown:
    """ 倒计时器 """

    instances = []  # type: list[CountDown]  # 实例的创建时间

    @classmethod
    def execute(cls) -> None:
        """ 类管理 """
        while True:
            time.sleep(1)
            now = time.time()
            for cd in tuple(cls.instances):
                if cd.create and now > cd.create + cd.countdown:
                    cls.instances.remove(cd)
                    if cd.command:
                        cd.command()

    def __init__(
            self,
            countdown: int,
            command=None  # type: function | None
    ) -> None:
        self.countdown = countdown
        self.command = command
        self.create = None
        self.instances.append(self)

    def reset(self) -> None:
        """ 重置 """
        self.create = time.time()

    def shutdown(self) -> None:
        """ 终止 """
        self.create = time.time() - self.countdown

    def run(self) -> None:
        """ 倒计时 """
        self.create = time.time()


class Server:
    """ 服务器 """

    output(INFO, '创建服务端套接字')
    server = socket.socket()
    output(INFO, '绑定端口: %s' % PORT)
    server.bind(('', PORT))
    output(INFO, '设置服务端监听最大数量: %d' % MAXIMUM)
    server.listen(MAXIMUM)

    @classmethod
    def load_data(cls) -> None:
        """ 加载用户数据 """
        for id in os.listdir('users'):
            User('users/%s/data.json' % id)

    @classmethod
    def accept(cls) -> None:
        """ 等待 """
        while True:
            try:
                client, retaddress = cls.server.accept()
                threading.Thread(
                    target=Client, args=(client, retaddress), daemon=True).start()
            except Exception as error:
                output(ERROR, error)

    @classmethod
    def sendmail(cls, mail: str, code: str) -> None:
        """ 发送邮件 """
        message = MIMEText(MSG % code, 'html', 'utf-8')
        message['Subject'] = TITLE  # 标题
        message['From'] = FROM  # 发件人
        message['To'] = mail
        smtp = smtplib.SMTP_SSL(HOST)
        file = open('AUTHORIZATION')
        smtp.login(USER, file.read())
        smtp.sendmail(SENDER, [mail], message.as_string())
        file.close()
        smtp.quit()

    @classmethod
    def input(cls, count: int = 1) -> None:
        """ 终端命令输入 """
        def put(msg: str, command=None) -> None:
            """ 输出 """
            print('\033[35mOut[%d]:\033[0m %s\n' % (count, msg))
            if command:
                command()

        print("\n%s v%s - Type '?' or 'help' for help\n" % (NAME, __version__))

        while True:
            match input('\033[32mIn [%d]:\033[0m ' % count):
                case '': continue
                case '?' | 'help': put(HELP)
                case 'quit' | 'exit' | 'shutdown': put('关闭 Questioner 服务器', exit)
                case 'users': put(list(_users))
                case 'countdown': put(len(CountDown.instances))
                case _: put('Unknow Command')
            count += 1


class _User:
    """ 用户基类 """

    def __init__(self, mail: str) -> None:
        self.mail = mail
        self.code = None
        self.countdown = None
        _users[self.mail] = self

    def random_code(self) -> str:
        """ 验证码 """
        self.code = ''.join(random.choice(CODES) for _ in range(6))
        if self.countdown:
            self.countdown.shutdown()
        self.countdown = CountDown(600, self.clean)
        return self.code

    def clean(self) -> None:
        """ 清空 """
        self.code = None
        self.countdown = None
        if type(self) != User:
            del _users[self.mail]


class User(_User):
    """ 用户 """

    def __init__(self, path: str) -> None:
        with open(path) as data:
            data = json.load(data)
        self.path = path
        self.nickname = data['nickname']
        self.mail = data['mail']
        self.password = data['password']
        self.id = data['id']
        self.code = None
        users[self.mail] = self

    @classmethod
    def new(cls, data: dict) -> None:
        """ 新用户 """
        del data['op'], data['code']
        init = INIT_DATA.copy()
        init.update(data)
        init['id'] = len(users)+1
        os.mkdir('users/%d' % init['id'])
        with open(path := 'users/%d/data.json' % init['id'], 'w') as file:
            json.dump(init, file, indent=4)
        User(path)
        output(INFO, '%s Register [id: %d]' % (init['mail'], init['id']))


class Client:
    """ 客户端 """

    def __init__(self, client: socket.socket, retaddress: tuple[str, int]) -> None:
        self.client = client
        self.client.settimeout(600)
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
            try:
                data = self.recv()
            except Exception as error:
                if type(error) != TimeoutError:
                    output(WARN, error)
                return self.close()

            match data['op']:
                case 'REFRESH': pass
                case 'QUIT': return self.close()
                case 'CODE':
                    if _users.get(data['mail']):
                        code = _users[data['mail']].random_code()
                    else:
                        code = _User(data['mail']).random_code()
                    try:
                        output(INFO, '发送验证码到 %s' % data['mail'])
                        Server.sendmail(data['mail'], code)
                    except:
                        output(WARN, '无法发送验证码到 %s！' % data['mail'])
                case 'REGISTER':
                    if _users.get(data['mail']):
                        if data['code'] == _users[data['mail']].code:
                            if not users.get(data['mail']):
                                User.new(data)
                                self.send(op='REGISTER', state='REGISTER_OK')
                            else:  # 账号已存在
                                self.send(op='REGISTER',
                                          state='REGISTER_REPEAT')
                        else:  # 验证码错误
                            self.send(op='REGISTER', state='REGISTER_ERROR')
                    else:  # 验证码失效
                        self.send(op='REGISTER', state='REGISTER_ERROR')
                case 'LOGIN':
                    if data['mode'] == 'PASSWORD':
                        if users.get(data['mail']):
                            if users[data['mail']].password == data['password']:
                                output(INFO, '%s Login' % data['mail'])
                                self.send(op='LOGIN', mode='PASSWORD',
                                          state='LOGIN_OK', data=None)
                            else:
                                self.send(op='LOGIN', mode='PASSWORD',
                                          state='LOGIN_ERROR')
                        else:
                            self.send(op='LOGIN', mode='PASSWORD',
                                      state='LOGIN_ERROR')
                    else:
                        if users.get(data['mail']):
                            if data['code'] == users.get(data['mail']).code:
                                output(INFO, '%s Login' % data['mail'])
                                self.send(op='LOGIN', mode='CODE',
                                          state='LOGIN_OK', data=None)
                            else:
                                self.send(op='LOGIN', mode='CODE',
                                          state='LOGIN_ERROR')
                        else:
                            self.send(op='LOGIN', mode='CODE',
                                      state='LOGIN_ERROR')


def main() -> None:
    """ 主函数 """
    output(INFO, '加载用户数据')
    Server.load_data()
    output(INFO, '启动服务端计时功能')
    threading.Thread(target=CountDown.execute, daemon=True).start()
    output(INFO, '启动客户端监听功能')
    threading.Thread(target=Server.accept, daemon=True).start()
    output(INFO, '启动服务端命令功能')
    Server.input()


if __name__ == '__main__':
    main()

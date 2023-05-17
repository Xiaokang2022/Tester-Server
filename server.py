""" 服务器 """
import socket
import sys
import threading
import time

from client import Client
from log import check_log, logger
from mail import Email
from randcode import Code
from timer import Countdown
from user import User

__version__ = '0.0.8'

print(hlep_doc := """
Questioner -- Python习题测试服务器
==================================

Query Command
-------------
? | help                        -> 指令帮助文档
thread_count                    -> 活跃线程数量
cd_count                        -> 计时器数量
client_count                    -> 客户端数量
code_count                      -> 验证码数量
user_count                      -> 用户数量
max_id                          -> 最大用户id
time                            -> 服务端运行时间
port                            -> 服务端端口
max_listen                      -> 最大监听数量
timer_interval                  -> 计时器检测间隔
smtp_server                     -> SMTP服务器地址
email_sender                    -> 邮件代发地址

Operation Command
-----------------
quit | exit | shutdown          -> 关闭服务器
run [command]                   -> 执行[子命令]
    User.data                   -> 查询用户数据[数据较大]
    User._load()                -> 重新加载用户数据
    Email.broadcast([msg])      -> 发送广播邮件消息
    Countdown.close()           -> 手动关闭计时器功能
    Countdown.launch()          -> 手动打开计时器功能
    Countdown.instances         -> 查询计时器数据
    Code.codes                  -> 查询验证码数据
    Client.connection           -> 查询客户端连接数据

========================================================
如果你想终止服务器, 请输入“quit”、“exit”或者“shutdown”
""")


class Server:
    """ 服务器 """

    server = None
    port = 32768
    max_listen = 128
    pack_size = 4096
    once = False
    _time = time.time()  # 启动时间

    @classmethod
    def launch(cls) -> None:
        """ 启动服务器 """
        try:
            logger.info('创建服务端套接字')
            cls.server = socket.socket()
        except Exception as error:
            logger.critical('服务器无法创建套接字, %s' % error)
            sys.exit()
        try:
            logger.info('绑定端口: %s' % cls.port)
            cls.server.bind(('', cls.port))
        except Exception as error:
            logger.critical('服务器无法绑定端口, %s' % error)
            sys.exit()
        try:
            logger.info('设置服务端最大监听数量: %s' % cls.max_listen)
            cls.server.listen(cls.max_listen)
        except Exception as error:
            logger.error('服务器无法设置最大监听数量, %s' % error)
        if cls.once is False:
            cls.once = True
            check_log()
            User.launch()
            threading.Thread(target=Countdown.launch).start()
            threading.Thread(target=cls.accept, daemon=True).start()
            Command.launch()

    @classmethod
    def gettime(cls) -> str:
        """ 计算服务端运行时间 """
        dt = time.time() - Server._time
        dt, ms = int(dt), (dt - int(dt)) * 1000
        day, dt = divmod(dt, 86400)
        hour, dt = divmod(dt, 3600)
        min, second = divmod(dt, 60)
        return '\033[35m%dd\033[36m%dh\033[32m%dm\033[33m%ds\033[0m%03dms' % (day, hour, min, second, ms)

    @classmethod
    def close(cls) -> None:
        """ 关闭服务器 """
        Countdown.close()
        Command.close()
        cls.server.close()
        logger.info('服务器终止运行！')

    @classmethod
    def accept(cls) -> None:
        """ 等待 """
        logger.info('监听功能启动')
        while True:
            try:
                threading.Thread(
                    target=Client, args=cls.server.accept(), daemon=True).start()
            except Exception as error:
                logger.warning('用户连接失败, %s' % error)


class Command:
    """ 指令输入类 """

    count = 0
    flag = True

    @classmethod
    def launch(cls) -> None:
        """ 启动指令输入操作 """
        logger.info('指令功能启动')
        cls.process()

    @classmethod
    def close(cls) -> None:
        """ 终止操作 """
        logger.info('指令功能关闭')
        cls.flag = False

    @classmethod
    def gettime(cls) -> str:
        """ 获取当前时间 """
        now = time.time()
        _time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now))
        ms = (now - int(now)) * 1000
        return '\033[36m%s.%03d\033[0m' % (_time, ms)

    @classmethod
    def refresh(cls) -> None:  # BUG
        """ 刷新命令行 """
        print('%s \033[32mIn [%d]\033[0m: ' %
              (cls.gettime(), cls.count), end=':::')

    @classmethod
    def INPUT(cls) -> str:
        """ 输入指令 """
        if msg := input('%s \033[32mIn [%d]\033[0m: ' % (cls.gettime(), cls.count)).strip():
            logger.info(msg)
            return msg
        return cls.INPUT()

    @classmethod
    def OUTPUT(cls, msg: str) -> None:
        """ 输出结果 """
        logger.info(msg)
        print('%s \033[31mOut[%d]\033[0m: %s' %
              (cls.gettime(), cls.count, msg))

    @classmethod
    def process(cls) -> None:
        """ 处理指令 """
        while cls.flag:
            cls.count += 1
            match msg := cls.INPUT():
                case 'quit' | 'exit' | 'shutdown':
                    cls.OUTPUT('服务器正在停止中...')
                    Server.close()
                case '?' | 'help': cls.OUTPUT(hlep_doc)
                case 'thread_count': cls.OUTPUT(threading.active_count())
                case 'cd_count': cls.OUTPUT(len(Countdown.instances))
                case 'code_count': cls.OUTPUT(len(Code.codes))
                case 'client_count': cls.OUTPUT(len(Client.connection))
                case 'max_id': cls.OUTPUT(User._id)
                case 'time': cls.OUTPUT(Server.gettime())
                case 'port': cls.OUTPUT(Server.port)
                case 'max_listen': cls.OUTPUT(Server.max_listen)
                case 'timer_interval': cls.OUTPUT(Countdown.interval)
                case 'user_count': cls.OUTPUT(len(User.data))
                case 'smtp_server': cls.OUTPUT(Email.smtp)
                case 'email_sender': cls.OUTPUT(Email.sender)
                case _:
                    if msg.startswith('run'):
                        try:
                            cls.OUTPUT(eval(msg[4:]))
                        except Exception as error:
                            cls.OUTPUT('无法执行该命令, %s' % error)
                    else:
                        cls.OUTPUT('Unknow Command: %s' % msg)


if __name__ == '__main__':
    logger.info('服务器正在启动中...')
    Server.launch()

""" 服务器常量 """

# 服务器

NAME = 'Questioner'  # 服务器名称
PORT = 32768  # 服务器端口
MAXIMUM = 128  # 监听最大数量
PACK_SIZE = 4096  # 单个包大小

# 日志

INFO = '\033[32mINFO\033[0m'  # 信息标识
WARN = '\033[33mWARN\033[0m'  # 警告标识
ERROR = '\033[31mERROR\033[0m'  # 错误标识

# 邮件

HOST = 'smtp.qq.com'  # QQ邮箱服务器地址
USER = '2951256653'  # 用户名
SENDER = '2951256653@qq.com'  # 邮件发送方邮箱地址
TITLE = 'Questioner服务器验证码'  # 标题
FROM = 'Questioner服务器'  # 发件人
CODES = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'  # 验证码可能值
MSG = """
<div style="font-family:楷体 ; background-color: lightyellow; border:3px solid black ;padding:10px">
    <h2 style="text-align: center;">Questioner服务器验证码</h2>
    <p style="text-align: center;">下面是您本次的验证码，10分钟内有效</p>
    <h1 style="text-align: center;">%s</h1>
    <p style="text-align: center;">若您未请求过验证码，那或许是他人误填了您的邮箱，请您忽略这封邮件</p>
</div>"""  # 信息基本格式

# 用户初始化数据

INIT_DATA = {
    'nickname': None,
    'mail': None,
    'password': None,
    'id': None
}

# 命令行帮助

HELP = """

%s -- Python习题测试服务器
==================================

Command
-------

? | help                -> 命令帮助文档
quit | exit | shutdown  -> 关闭服务器
users                   -> 临时连接
countdown               -> 计时器数量（可用验证码数量）

如果你想终止服务器，请输入“quit”、“exit”或者“shutdown”""" % NAME

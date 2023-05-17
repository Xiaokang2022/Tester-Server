""" 验证码功能 """
import random

from log import logger
from timer import Countdown


class Code:
    """ 验证码类 """

    _code = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    codes = {}  # type: dict[str, Code]

    def __init__(self, mail: str, length: int = 6) -> None:
        self.mail = mail
        self.value = ''.join(random.choices(Code._code, k=length))
        Code.codes[self.value] = self
        self.cd = Countdown(600, self.destroy)

    def cancel(self) -> None:
        """ 取消验证码（已使用） """
        self.cd.over()

    def destroy(self) -> None:
        """ 释放验证码 """
        del Code.codes[self.value]


if __name__ == '__main__':
    logger.debug('#=== 验证码功能测试 ===#')
    for _ in range(5):
        print(Code().value())
    logger.debug('#=== 验证码功能测试 ===#')

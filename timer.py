""" 计时功能 """
import threading
import time
from typing import Callable

from log import logger


class Countdown:
    """ 倒计时类 """

    instances = []  # type: list[Countdown]
    flag = True
    thread = None
    interval = 1  # 检测时间间隔

    def __init__(self, duration: float, func: Callable, *args, **kw) -> None:
        self.end = time.time() + duration
        self.func = lambda: func(*args, **kw)
        Countdown.instances.append(self)
        Countdown.instances.sort(key=lambda cd: cd.end)

    def over(self) -> None:
        """ 倒计时结束 """
        self.destroy()
        self.func()

    def destroy(self) -> None:
        """ 释放/取消计时器 """
        try:
            Countdown.instances.remove(self)
        except Exception as error:
            logger.warning('计时器资源释放失败, %s' % error)

    @classmethod
    def launch(cls) -> None:
        """ 启动计时器 """
        try:
            logger.info('计时功能启动')
            cls.thread = threading.Thread(target=cls.check)
            cls.thread.start()
        except Exception as error:
            logger.error('无法启动计时器功能, %s' % error)

    @classmethod
    def close(cls) -> None:
        """ 关闭计时器 """
        logger.info('计时功能关闭')
        cls.flag = False
        cls.instances.clear()

    @classmethod
    def check(cls) -> None:
        """ 检查计时器 """
        while cls.flag:
            now = time.time()
            for _time in tuple(cls.instances):
                if _time.end < now:
                    _time.over()
                else:
                    break
            time.sleep(cls.interval)


if __name__ == '__main__':
    logger.debug('#=== 计时功能测试 ===#')
    Countdown(5, print, '5秒倒计时结束')
    Countdown(10, Countdown.close)  # 10 秒关闭
    Countdown.launch()
    Countdown.thread.join()
    logger.debug('#=== 计时功能测试 ===#')

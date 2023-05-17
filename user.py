""" 用户功能 """
import json
import os
import time
from copy import deepcopy

from log import logger

init_data = {
    'id': None,  # int 唯一标识符
    'mail': None,  # str 邮箱
    'psd': None,  # str 密码
    'level': None,  # int 等级
    'name': None,  # str 昵称
    'sex': None,  # bool 性别
    'age': None,  # int 年龄
    'profile': None,  # str 简介
    'join_time': None,  # float 注册加入时间
    'friend': [],  # list[int] 好友数据
    'cache': {},  # dict[int, list[str]] 缓存消息
}


class User:
    """ 用户类 """

    data = {}  # type: dict[str, dict[str, list | dict | str | float | bool]]
    _id = 0  # 用户数量（最大id）

    def __init__(self, mail: str) -> None:
        self.mail = mail

    def clear_cache(self) -> None:
        """ 清空缓存消息 """
        User.data[self.mail]['cache'].clear()
        self.modify(self.mail)

    def chat(self, to: int, msg: str) -> None:
        """ 聊天 """
        if User.data[to]['cache'].get(self.mail, None):
            User.data[to]['cache'][self.mail].append(msg)
        else:
            User.data[to]['cache'][self.mail] = [msg]

    @classmethod
    def delete(cls, id: int) -> None:
        """ 删除用户 """
        try:
            os.remove('./users/%d.json' % id)
            logger.info('用户数据已删除(id: %d)' % id)
        except Exception as error:
            logger.warning('用户删除失败, %s' % error)

    @classmethod
    def friend_del(cls, mails: tuple[str, str]) -> None:
        """ 删除好友 """
        for i in range(2):
            cls.data[mails[i-1]]['friend'].remove(mails[i])
            cls.modify(mails[i-1])

    @classmethod
    def friend_add(cls, mails: tuple[str, str]) -> None:
        """ 添加好友 """
        for i in range(2):
            cls.data[mails[i-1]]['friend'].append(mails[i])
            cls.modify(mails[i-1])

    @classmethod
    def modify(cls, mail: str, **kw) -> None:
        """ 修改文件 """
        try:
            cls.data[mail].update(**kw)
            id = cls.data[mail]['id']
            with open('./users/%d.json' % id) as user:
                json.dump(cls.data[mail], user, indent=4)
        except Exception as error:
            logger.warning('用户文件修改失败, %s' % error)

    @classmethod
    def getnewid(cls) -> int:
        """ 获取新的id """
        cls._id += 1
        return cls._id

    @classmethod
    def new(cls, name: str, mail: str, psd: str) -> None:
        """ 新用户 """
        try:
            id = cls.getnewid()
            data = deepcopy(init_data)
            data.update(name=name, mail=mail, psd=psd, id=id,
                        level=1, join_time=time.time())
            with open('./users/%d.json' % id, 'w', encoding='utf-8') as user:
                json.dump(data, user, indent=4)
            cls.data[mail] = data
            logger.info('新用户已创建(id: %d)' % id)
        except Exception as error:
            logger.warning('新用户创建失败, %s' % error)

    @classmethod
    def _load(cls) -> None:
        """ 加载数据 """
        logger.info('加载用户数据')
        for file in os.listdir('./users'):
            with open('./users/%s' % file, encoding='utf-8') as user:
                data = json.load(user)
                cls.data[data['mail']] = data
                if (id := data['id']) > cls._id:
                    cls._id = id

    @classmethod
    def launch(cls) -> None:
        """ 启动用户功能 """
        try:
            logger.info('用户功能启动')
            cls._load()
        except Exception as error:
            logger.error('无法启动用户功能, %s' % error)


if __name__ == '__main__':
    logger.debug('#=== 用户功能测试 ===#')
    User.launch()
    User.new('Tester', '18888888888@.com', '123')
    print(User._id)
    User.delete(2)
    logger.debug('#=== 用户功能测试 ===#')

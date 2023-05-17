""" 邮件功能 """
import json
import os
import smtplib
from email import utils
from email.mime import text

from log import logger


class Email:
    """邮件"""

    smtp = 'smtp.qq.com'
    sender = '2951256653@qq.com'
    msg_from = "QuestionerServer", sender
    with open('./email/code_email.html') as codemsg:
        codemsg = codemsg.read()
    with open('./email/register_email.html') as regmsg:
        regmsg = regmsg.read()

    def __init__(self, addr: str, msg: str, title: str, name: str = '') -> None:
        self.addr = addr
        self.name = name if name else addr
        self.msg = self._build_text(name, addr, msg, title)

    def send(self) -> None:
        """ 发送邮件 """
        try:
            smtp_ssl = smtplib.SMTP_SSL(self.smtp, 465)
            smtp_ssl.login(self.sender, open("AUTHORIZATION").read())
            smtp_ssl.sendmail(Email.sender, self.addr, self.msg.as_string())
            logger.info('发送邮件到 %s' % self.addr)
        except Exception as error:
            logger.warning('无法发送邮件到 %s, %s' % (self.addr, error))
        finally:
            smtp_ssl.close()

    @classmethod
    def _build_text(cls, name: str, addr: str, msg: str, title: str) -> text.MIMEText:
        """ 生成邮件 """
        msg = text.MIMEText(msg)
        msg['To'] = utils.formataddr((name, addr))
        msg['From'] = utils.formataddr(cls.msg_from)
        msg["Subject"] = title
        return msg

    @classmethod
    def build_codemsg(cls, name: str, code: str) -> str:
        """ 生成验证码邮件 """
        return cls.codemsg % (name, code)

    @classmethod
    def build_regmsg(cls, name: str) -> str:
        """ 生成注册成功邮件 """
        return cls.regmsg % name

    @classmethod
    def broadcast(cls, msg: str) -> None:
        """ 邮件广播 """
        try:
            smtp_ssl = smtplib.SMTP_SSL(cls.smtp, 465)
            smtp_ssl.login(cls.sender, open("AUTHORIZATION").read())
            for userfile in os.listdir('./users'):
                with open('./users/' + userfile, encoding='utf-8') as user:
                    data = json.load(user)
                    smtp_ssl.sendmail(cls.sender, data['mail'], cls._build_text(
                        data['name'], data['mail'], msg, 'Questioner服务器广播').as_string())
            logger.info('邮件广播: %s' % msg)
        except Exception as error:
            logger.warning('无法进行邮件广播操作, %s' % error)
        finally:
            smtp_ssl.close()


if __name__ == "__main__":
    logger.debug('#=== 邮件功能测试 ===#')
    Email(Email.sender, Email.build_codemsg(
        'Admin', '666666'), 'Questioner服务器验证码').send()
    Email.broadcast('Broadcast Test')
    logger.debug('#=== 邮件功能测试 ===#')

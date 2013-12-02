#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 F2E.im
# Do have a faith in what you're doing.
# Make your life a story worth telling.

import os
import sys
import smtplib
import email
from email.mime.text import MIMEText

charset = 'utf-8'
send_mail_host = 'smtp.exmail.qq.com'
send_mail_user = 'wutong@sicun.org'
send_mail_pswd = os.getenv("WUTONG_EMAIL_PASSWD")
send_mail_user_name = u'梧桐'
send_mail_suffix = 'sicun.org'


def connectToSmtpServer():
    stp = smtplib.SMTP()
    stp.connect(send_mail_host)
    stp.login(send_mail_user,send_mail_pswd)
    return stp

def send(sub, content, reciver):
    if '@' in send_mail_user:
        email_address = send_mail_user
    else:
        email_address = send_mail_user + '@' + send_mail_suffix
    send_mail_address = send_mail_user_name + '<' + email_address + '>'
    msg = email.mime.text.MIMEText(content,'html',charset)
    msg['Subject'] = email.Header.Header(sub,charset)
    msg['From'] = send_mail_address
    msg['to'] = to_adress = reciver
    try:
        stp = connectToSmtpServer()
        stp.sendmail(send_mail_address,to_adress,msg.as_string())
        stp.close()
        return True
    except Exception,e:
        print(e)
        return False

if send_mail_pswd is None:
    send_mail_pswd = raw_input("Please input wutong email password:")
    connectToSmtpServer().close()

if __name__ == "__main__":
    send(u"测试主题", u"测试内容", "wutong@sicun.org")


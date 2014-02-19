#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import functools
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler
from tornado.escape import json_encode
from tornado import gen
import tornadoredis as redis
from lib.session import Session
from model import user, group, article
import lib.util


def authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            raise Exception('not login')
        return method(self, *args, **kwargs)
    return wrapper

def catch_exception(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except Exception as e:
            self.write_errmsg(e)
    return wrapper


def login(self, user_id=None, user=None):
    user = user or self.get_current_user(user_id)
    self.session['uid'] = user['uid']
    cnt = self.muser.get_unread_msg_count(user['uid'])
    user = self.get_pure_user()
    user['msg_count'] = cnt
    return user


class BaseHandler(RequestHandler):
    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        self.session = Session(self)
        self.db = self.application.db
        if not isinstance(self, WebSocketHandler):
            # record last view url
            self.set_cookie('last_view', self.request.uri)

    def on_finish(self):
        self.session.save()

    def get_current_user(self, user_id=None):
        """
        if you want a cached version of `get_current_user`, you can use
        `current_user`
        """
        return self.muser.get_user(user_id or self.user_id)

    def get_pure_user(self, user=None):
        """
        被客户端接收的用户信息, 不包含权限等客户端无关信息
        """
        user = user or self.current_user
        return {
            'nickname': user['nickname'],
            'avatar': user['avatar'],
            'intro': user['intro'],
            'motto': user['motto'],
        }

    @property
    def user_id(self):
        return self.session.get("uid")

    @property
    def muser(self):
        """
        model of user
        """
        if not hasattr(self, "_user_model"):
            self._user_model = user.UserModel(self.db)
        return self._user_model

    @property
    def mgroup(self):
        if not hasattr(self, "_group_model"):
            self._group_model = group.GroupModel(self.db)
        return self._group_model

    @property
    def marticle(self):
        if not hasattr(self, "_article_model"):
            self._article_model = article.ArticleModel(self.db)
        return self._article_model

    def get_argument(self, name, default=None):
        return super(BaseHandler, self).get_argument(name, default)

    def has_argument(self, name):
        return name in self.request.arguments

    @property
    def args(self):
        if not hasattr(self, '_args'):
            self._args = {}
        return self._args

    def get_args(self, *args, **newnames):
        for name in args:
            newname = newnames.get(name, name)
            self.get_arg(name, newname=newname)
        return self.args

    def get_arg(self, name, default=None, newname=None):
        value = self.get_argument(name, default)
        name = newname or name
        self.args[name] = value
        return value

    def set_arg(self, name, value):
        if self.has_arg(name) is None:
            return None
        self.args[name] = value
        return value

    def has_arg(self, name):
        return self.args.get(name)

    def check_arg(self, name, func, result=True, errmsg=None):
        """
        调用`func`检查指定参数. 若参数不存在, 则返回`default`, 否则返回`func`返回值
        """
        value = self.args.get(name)
        if value and func(value) != result:
            if not errmsg:
                errmsg = 'invalid ' + name
            raise Exception(errmsg)

    @property
    def ip(self):
        return self.request.remote_ip

    def get_module_path(self):
        module_path = os.path.join(self.get_template_path(), "modules")
        return module_path

    def render_module_string(self, module_name, **kwargs):
        module_path = self.get_module_path()
        return self.render_string(os.path.join(module_path, module_name), **kwargs)

    def render_404_page(self):
        self.render('404.html')

    def get(self):
        self.render_404_page()

    def post(self):
        self.write_error(403)

    def message2json(self, msg, errno=0):
        return '{"msg": "%s", "errno": "%s"}' % (msg, errno)

    def write_result(self, msg='', errno=0):
        """
        :errno 错误码, 0=正常, 0<出错, 0>出错但未设置错误码
        """
        self.write(self.message2json(msg, errno))

    def write_errmsg(self, msg='', errno=-1):
        self.write_result(str(msg), errno)

    def write_json(self, data, errmsg='unknown error'):
        """
        若data不为空值, 发送err指定的错误信息
        """
        if data is None or data == '':
            self.write_errmsg(errmsg)
            return
        self.write(json_encode(data))


class SessionBaseHandler(BaseHandler):
    send_client = redis.Client()
    send_client.connect()

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        self._channel = value

    def format_message(self, message):
        """
        do user has send permission ?
        is message invalid ?
        return saveable message
        """
        raise NotImplementedError

    def save_message(self, message):
        """
        save message to database
        """
        raise NotImplementedError

    def send_message(self, message):
        try:
            message = self.format_message(message)
            message = self.save_message(message)
            self.send_client.publish(self.channel, message)
        except Exception as e:
            self.write_errmsg(e)

    @gen.engine
    def listen(self):
        self.client = redis.Client()
        self.client.connect()
        yield gen.Task(self.client.subscribe, self.channel)
        self.client.listen(self._on_message)

    def _on_message(self, message):
        try:
            if message.kind == 'message':
                self.write(json_encode(message.body))
            elif message.kind == 'disconnect':
                # Do not try to reconnect, just raise a error
                raise Exception('Redis server error')
        except Exception as e:
            self.write_errmsg(e)

    def on_close(self):
        """
        Don't call this function in `RequestHandler`
        """
        if self.client.subscribed:
            self.client.unsubscribe(self.channel)
            self.client.disconnect()

    def write(self, message):
        if hasattr(self, 'write_message'):
            return self.write_message(message)
        else:
            return super(SessionHandler, self).write(message)

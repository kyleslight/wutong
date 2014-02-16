#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler
from tornado.escape import json_encode
from lib.session import Session
from model import user, group, article
import lib.util


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
        if not self.has_arg(name):
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

    def write_result(self, msg='', errno=0):
        """
        :errno 错误码, 0=正常, 0<出错, 0>出错但未设置错误码
        """
        self.write('{"msg": "%s", "errno": "%s"}' % (msg, errno))

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

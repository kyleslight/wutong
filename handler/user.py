#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado import escape
from tornado.web import authenticated
from base import BaseHandler
from lib.util import createpasswd

class UserBaseHandler(BaseHandler):

    @property
    def model(self):
        return self.usermodel

    def set_authenticated(self, uid):
        self.set_secure_cookie("uid", str(uid), 5, httponly=True)


class LoginHandler(UserBaseHandler):

    def post(self):
        account = self.get_argument("username", None)
        password = self.get_argument("password", None)

        if self.do_login(account, password):
            self.write("success")
        else:
            self.write("failed")

    def do_login(self, account, password):
        user_id = self.model.do_login_by_account_and_password(account=account, password=password)
        if user_id:
            self.set_authenticated(user_id)
        return user_id


class LogoutHandler(UserBaseHandler):

    def post(self):
        self.clear_cookie("uid")


class RegisterHandler(UserBaseHandler):

    def post(self):
        penname = self.get_argument("username", None)
        password = self.get_argument("password", None)
        email = self.get_argument("email", None)

        hashuid = self.do_register(email=email, penname=penname, password=password)
        if hashuid:
            self.write("success")
            self.send_mail(hashuid)
        else:
            self.write("failed")

    def do_register(self, email, password, penname):
        hashuid = self.model.do_register(email=email, password=password, penname=penname)
        return hashuid

    def send_mail(self, hashuid):
        url = "http://localhost:8888/account/check?r=" + hashuid
        self.write(url)


class UserinfoHandler(UserBaseHandler):

    @authenticated
    def get(self):
        userinfo = self.get_current_user()
        userinfo["register_date"] = str(userinfo["register_date"])
        userinfo = escape.json_encode(userinfo)
        self.write(userinfo)


class CheckMailHandler(UserBaseHandler):

    def get(self):
        hashuid = self.get_argument("r", None)
        uid = self.check_mail(hashuid)
        if uid:
            self.set_authenticated(uid)
            self.write("success")
        else:
            self.write("error")

    def check_mail(self, hashuid):
        return self.model.do_activate_by_hashuid(hashuid)


class HomeHandler(UserBaseHandler):

    def get(self):
        pass

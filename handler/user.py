#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado import escape
from tornado.web import authenticated
from lib.session import Session
from lib import sendmail
from base import BaseHandler

class UserBaseHandler(BaseHandler):

    @property
    def model(self):
        return self.usermodel

    def set_authenticated(self, uid):
        self.session["uid"] = uid


class LoginHandler(UserBaseHandler):

    def get(self):
        # @authenticated will call this function
        pass

    def post(self):
        account = self.get_argument("username", None)
        password = self.get_argument("password", None)

        uid = self.do_login(account, password)
        if uid:
            self.write("success")
        else:
            self.write("failed")

    def do_login(self, account, password):
        user_id = self.model.do_login(account=account, password=password)
        if user_id:
            self.set_authenticated(user_id)
        return user_id


class LogoutHandler(UserBaseHandler):

    def post(self):
        self.session.clear()
        self.write("success")


class RegisterHandler(UserBaseHandler):

    def post(self):
        penname = self.get_argument("username", None)
        password = self.get_argument("password", None)
        email = self.get_argument("email", None)

        hashuid = self.do_register(email, penname, password)
        if hashuid:
            self.send_mail(email, hashuid)
        else:
            self.write("failed")

    def do_register(self, email, penname, password):
        hashuid = self.model.do_register(email, penname, password)
        return hashuid

    def send_mail(self, email, hashuid):
        title = u"欢迎加入梧桐"
        content = u"{url}".format(
            url = "http://localhost:8888/account/check?r=" + hashuid
        )
        if sendmail.send(title, content, email):
            self.write("success")
        else:
            self.write("failed")


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
        self.redirect("/")

    def check_mail(self, hashuid):
        return self.model.do_activate(hashuid)


class HomeHandler(UserBaseHandler):

    def get(self):
        self.write("user home")

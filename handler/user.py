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

    def is_admin(self):
        if not hasattr(self, "_permission"):
            self._permission = self.get_user_permission(self.user_id)
        return self._permission.get("is_admin", False)


class HomeHandler(UserBaseHandler):
    def get(self, penname):
        uid = self.model.get_uid(penname)
        user_info = self.model.get_user_info(uid)
        self.render('user.html', user=user_info)


class PermissionHandler(UserBaseHandler):
    @authenticated
    def post(self):
        check = self.get_argument("check_permission")
        if check == "is_admin":
            if self.is_admin():
                self.write("true")
            else:
                self.write("false")


class LoginHandler(UserBaseHandler):
    def get(self):
        # @authenticated will call this function
        pass

    def post(self):
        account = self.get_argument("username")
        password = self.get_argument("password")

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
        penname = self.get_argument("username")
        password = self.get_argument("password")
        email = self.get_argument("email")

        hashuid = self.do_register(email, penname, password)
        if hashuid:
            self.send_mail(email, hashuid)
        else:
            self.write("failed")

    def do_register(self, email, penname, password):
        hashuid = self.model.do_register(email, penname, password)
        return hashuid

    def send_mail(self, email, hashuid):
        if self.settings["debug"]:
            self.model.do_activate(hashuid)
            self.write("success")
            return
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

    # update user info
    @authenticated
    def post(self):
        userinfo = self.get_current_user()
        email = self.get_argument('email')
        penname = self.get_argument('penname')
        phone = self.get_argument('phone')

        res = self.model.is_user_exists(email=email,
                                        penname=penname,
                                        phone=phone)
        if res:
            self.write('exists')
            return
        else:
            userinfo['email'] = email or userinfo['email']
            userinfo['penname'] = penname or userinfo['penname']
            userinfo['phone'] = phone or userinfo['phone']

        userinfo['realname'] = self.get_argument('realname', userinfo['realname'])
        userinfo['sex'] = self.get_argument('sex', userinfo['sex'])
        userinfo['age'] = self.get_argument('age', userinfo['age'])
        userinfo['address'] = self.get_argument('address', userinfo['address'])
        userinfo['intro'] = self.get_argument('intro', userinfo['intro'])
        userinfo['motton'] = self.get_argument('motton', userinfo['motton'])
        userinfo['avatar'] = self.get_argument('avatar', userinfo['avatar'])

        self.model.update_user_info(userinfo['uid'], **userinfo)


class CheckMailHandler(UserBaseHandler):
    def get(self):
        hashuid = self.get_argument("r")
        uid = self.check_mail(hashuid)
        if uid:
            self.set_authenticated(uid)
            self.write("success")
        else:
            self.write("error")
        self.redirect("/")

    def check_mail(self, hashuid):
        return self.model.do_activate(hashuid)

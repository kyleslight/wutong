#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random
from tornado.escape import json_encode
from tornado.web import authenticated
from lib import sendmail
from lib import util
from base import BaseHandler


class UserBaseHandler(BaseHandler):
    @property
    def model(self):
        return self.usermodel

    @property
    def penname(self):
        return self.get_current_user()['penname']

    def set_authenticated(self, uid):
        self.session["uid"] = uid

    def is_admin(self):
        if not hasattr(self, "_permission"):
            self._permission = self.get_user_permission(self.user_id)
        return self._permission.get("is_admin", False)


class IndexHandler(UserBaseHandler):
    def get(self):
        url = self.get_cookie('last_view')
        self.redirect(url)


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
            user_info = self.model.get_user_info(uid)
            self.write(json_encode(user_info))
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
    def set_random_avatar(self, penname):
        avatar_dir = self.settings['avatar_path']
        random_path = os.path.join(avatar_dir, 'random')
        avatar_path = os.path.join(random_path,
                                   random.choice(os.listdir(random_path)))

        with open(avatar_path, 'r') as avatar_fp:
            avatar = util.genavatar(avatar_fp, avatar_dir, penname)
            return self.model.update_user_avatar_by_penname(penname, avatar)

    def post(self):
        penname = self.get_argument("username")
        password = self.get_argument("password")
        email = self.get_argument("email")

        hashuid = self.do_register(email, penname, password)
        if hashuid:
            self.set_random_avatar(penname)
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
            url = "http://localhost:8888/account/check?activate_account&v=" + hashuid
        )
        if not sendmail.send(title, content, email):
            self.write("failed")


class AccountCheckHandler(UserBaseHandler):
    def get(self):
        args = self.request.arguments
        if 'activate_account' in args:
            self.activate_account_by_email()
        elif 'is_account_exists' in args:
            self.is_account_exists()

    def activate_account_by_email(self):
        hashuid = self.get_argument('v')
        uid = self.model.do_activate(hashuid)
        if uid:
            self.set_authenticated(uid)
        else:
            self.write("failed")
        self.redirect("/")

    def is_account_exists(self):
        account = self.get_argument('v')
        uid = self.model.get_uid(account)
        self.write('true' if uid else 'false')


class UserinfoHandler(UserBaseHandler):
    @authenticated
    def get(self):
        userinfo = self.get_current_user()
        userinfo["register_date"] = str(userinfo["register_date"])
        userinfo = json_encode(userinfo)
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
        userinfo['sex'] = bool(self.get_argument('sex', userinfo['sex']))
        userinfo['age'] = self.get_argument('age', userinfo['age'])
        userinfo['address'] = self.get_argument('address', userinfo['address'])
        userinfo['intro'] = self.get_argument('intro', userinfo['intro'])
        userinfo['motton'] = self.get_argument('motton', userinfo['motton'])
        # userinfo['avatar'] = self.get_argument('avatar', userinfo['avatar'])

        self.model.update_user_info(userinfo['uid'], **userinfo)


class AvatarHandler(UserBaseHandler):
    @authenticated
    def post(self):
        # max avatar file is 10Mb
        self.max_file_size = 1000000

        if not "avatar" in self.request.files:
            self.write('failed')
            return
        try:
            filesize = int(self.request.headers['Content-Length'])
            if filesize > self.max_file_size:
                self.write('exceed')
                return
            avatar = {
                "name": self.penname,
                "request": self.request.files['avatar'][0],
            }
            avatar["data"] = avatar['request']['body'],
            avatar["suffix"] = util.filesuffix(avatar['request']['filename'])
            avatar["name"] = util.addsuffix(avatar["name"], avatar["suffix"])
            with StringIO.StringIO(avatar["data"]) as avatar_fp:
                avatar_dir = self.settings['avatar_path']
                avatar_name = util.genavatar(avatar_fp,
                                             avatar_dir,
                                             avatar["name"])
                self.write(avatar_name)
                return
        except:
            pass
        self.write('failed')


class MemoHandler(UserBaseHandler):
    @authenticated
    def get(self):
        page = self.get_argument('page', 1)
        size = self.get_argument('size', 100)

        offset = (page - 1) * size
        memos = self.model.get_memos(self.user_id, limit=size, offset=offset)
        memos = json_encode(memos)
        self.write(memos)

    @authenticated
    def post(self):
        title = self.get_argument('title')
        content = self.get_argument('content')

        memo_id = self.model.create_memo(self.user_id, title, content)
        memo = self.model.get_memo(memo_id)
        self.write(json_encode(memo))


class UpdateMemoHandler(UserBaseHandler):
    @authenticated
    def get(self):
        memo_id = self.get_argument('memo_id')

        memo = self.model.get_memo(memo_id)
        self.write(json_encode(memo))

    @authenticated
    def post(self):
        memo_id = self.get_argument('memo_id')
        title = self.get_argument('title')
        content = self.get_argument('content')

        if self.model.update_memo(self.user_id, memo_id, title, content):
            memo = self.model.get_memo(memo_id)
            self.write(json_encode(memo))
        else:
            self.write('failed')


class DeleteMemoHandler(UserBaseHandler):
    @authenticated
    def post(self):
        memo_id = self.get_argument('memo_id')

        if not self.model.delete_memo(self.user_id, memo_id):
            self.write('failed')


class CollectionHandler(UserBaseHandler):
    def add_collection(self, article_id):
        return self.create_article_collection(self.user_id, article_id)

    def get_collections(self, page_id=0):
        return self.model.get_collections(self.user_id, offset=page_id)

    @authenticated
    def get(self):
        collections = self.get_collections()
        self.write(json_encode(collections))

    @authenticated
    def post(self):
        article_id = self.get_argument('article_id')
        self.write(self.add_collection(article_id))


class AutoCompletionHandler(UserBaseHandler):
    def get(self):
        query = self.get_argument('q')

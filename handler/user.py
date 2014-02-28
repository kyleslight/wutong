#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import random
from sys import getsizeof
from tornado.web import asynchronous, gen_log
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado import gen
from lib import sendmail
from lib import util
from base import BaseHandler, authenticated, catch_exception, login
import userfile


class IndexHandler(BaseHandler):
    def get(self):
        self.render('home.html')


class HomeHandler(BaseHandler):
    def get(self, nickname):
        if not self.muser.is_nickname_exist(nickname):
            self.render_404_page()
            return
        user = self.current_user
        if user and user['nickname'] == nickname:
            editable = True
        else:
            editable = False
        user = self.muser.get_user_homepage(nickname)
        user['motto'] = user['motto'] or ''
        user['editable'] = editable
        self.render('user.html', user=user)


class LoginHandler(BaseHandler):
    def get(self):
        self.write_errmsg('need login')

    @catch_exception
    def post(self):
        nickname_or_email = self.get_argument("username")
        password = self.get_argument("password")

        if not util.is_email(nickname_or_email) and util.has_illegal_char(nickname_or_email):
            self.write_errmsg('illegal nickname')
            return
        user = self.muser.do_login(nickname_or_email, password)
        user = login(self, user=user)
        self.write_json(user)


class LogoutHandler(BaseHandler):
    def post(self):
        self.session.clear()


class RegisterHandler(BaseHandler):
    def notify_user(self):
        title = "加入梧桐"
        brief = """欢迎来到梧桐这个有爱的大家庭～，
                   希望您能在这里不断分享与提升自我。
                   在使用梧桐前请务必阅读我们的文档
                   <a href="/a/1">梧桐指南</a>"""
        self.muser.create_message(self.user_id, title, brief, type='1')

    @catch_exception
    def post(self):
        nickname = self.get_arg('nickname')
        password = self.get_arg('password')
        email = self.get_arg('email')

        self.check_arg('nickname', util.has_illegal_char, result=False)
        self.check_arg('email', util.is_email)
        user_id = self.muser.do_register(nickname, password, email)
        avatar = self.set_random_avatar(nickname)
        self.muser.update_user_info(user_id, avatar=avatar)
        self.notify_user()
        self.send_mail(email, user_id)
        # 前端负责登录
        # user = login(self, user_id=user_id)
        # self.write_json(user)

    def set_random_avatar(self, nickname):
        avatar_dir = self.settings['avatar_path']
        random_dir = os.path.join(avatar_dir, 'random')
        filepath = os.path.join(
            random_dir,
            random.choice(os.listdir(random_dir))
        )
        bindata = open(filepath, 'r').read()
        filename = util.add_suffix(nickname, 'png')
        savepath = os.path.join(avatar_dir, filename)
        avatar = userfile.genavatar(bindata, savepath)
        return util.get_path_url(avatar)

    def send_mail(self, email, user_id):
        if self.settings['debug']:
            self.muser.do_activate_account(user_id)
            return
        title = u'欢迎加入梧桐'
        content = u'{proto}://{host}/{path}'.format(
            proto=self.request.protocol,
            host=self.request.host,
            path='account?activate_account&v=&next=/' + util.encrypt(user_id)
        )
        if not sendmail.send(title, content, email):
            errmsg = "send email to '%s' error" % email
            gen_log.error(errmsg)
            raise Exception(errmsg)


class AccountHandler(BaseHandler):
    @catch_exception
    def get(self):
        """
        若成功返回相关信息或1, 失败返回错误信息或0
        """
        if self.has_argument('activate_account'):
            self.activate_account()
        elif self.has_argument('check_username'):
            self.check_username()
        elif self.has_argument('check_email'):
            self.check_email()
        url = self.get_argument('next')
        if url:
            self.redirect(url)

    def activate_account(self):
        value = self.get_argument('v')
        user_id = util.decrypt(value)
        self.muser.do_activate_account(user_id)
        user = login(self, user_id=user_id)
        self.write_json(user)

    def check_username(self):
        nickname = self.get_argument('v')
        if nickname and self.muser.is_nickname_exist(nickname):
            self.write_result('1')
        else:
            self.write_result('0')

    def check_email(self):
        email = self.get_argument('v')
        if email and self.muser.is_email_exist(email):
            self.write_result('1')
        else:
            self.write_result('0')


class UserinfoHandler(BaseHandler):
    @catch_exception
    @authenticated
    def get(self):
        user = login(self, user=self.current_user)
        self.write_json(user)

    @catch_exception
    @authenticated
    def post(self):
        """
        用户信息修改, 不处理头像与密码
        """
        self.get_args('nickname', 'email', 'realname',
                      'phone', 'birthday', 'sex',
                      'address', 'intro', 'motto')
        self.check_arg('nickname', util.has_illegal_char, result=False)
        self.check_arg('email', util.is_email)
        self.check_arg('realname', util.is_english_or_chinese)
        self.check_arg('phone', util.is_phone)
        self.check_arg('birthday', util.is_time)
        self.check_arg('sex', util.is_bool)
        self.check_arg('address', self.is_address)
        self.check_arg('nickname', self.muser.is_nickname_exist,
                       result=False,
                       errmsg='nickname exist')
        self.check_arg('email', self.muser.is_email_exist,
                       result=False,
                       errmsg='email exist')
        sex = self.get_arg('sex')
        self.set_arg('sex', util.get_bool(sex))
        self.do_update()

    def is_address(self, value):
        # TODO
        return True

    def do_update(self):
        user = self.current_user
        self.muser.update_user_info(user['uid'], **self.args)


class MemoHandler(BaseHandler):
    @catch_exception
    @authenticated
    def get(self):
        memo_id = self.get_argument('id')
        if memo_id:
            memo = self.muser.get_memo(self.user_id, memo_id)
            self.write_json(memo)
        else:
            page = int(self.get_argument('page', 1))
            size = int(self.get_argument('size', 100))
            memos = self.muser.get_memos(self.user_id, page, size)
            self.write_json(memos)

    @catch_exception
    @authenticated
    def post(self):
        if self.has_argument('create'):
            self.do_create()
        elif self.has_argument('update'):
            self.do_update()
        elif self.has_argument('delete'):
            self.do_delete()

    def get_title_and_content(self):
        title = self.get_argument('title')
        content = self.get_argument('content')

        if not title and not content:
            raise Exception('empty input')
        elif not title and content:
            title = util.get_abstract_str(content)
        elif title and not content:
            content = title
        return title, content

    def do_create(self):
        title, content = self.get_title_and_content()
        memo = self.muser.create_memo(self.user_id, title, content)
        self.write_json(memo)

    def do_update(self):
        title, content = self.get_title_and_content()
        memo_id = self.get_argument('id')
        memo = self.muser.update_memo(self.user_id, memo_id, title, content)
        self.write_json(memo)

    def do_delete(self):
        memo_id = self.get_argument('id')
        self.muser.delete_memo(self.user_id, memo_id)


class CollectionHandler(BaseHandler):
    @catch_exception
    @authenticated
    def get(self):
        collection_type = self.get_argument('type')
        if self.has_argument('check'):
            relevant_id = int(self.get_argument('relevant_id'))
            is_collected = self.muser.has_collected(self.user_id, collection_type, relevant_id)
            self.write_result(is_collected)
            return
        page = int(self.get_argument('page', 1))
        size = int(self.get_argument('size', 5))
        collections = self.muser.get_collections(self.user_id, collection_type, page, size)
        self.write_json(collections)

    @catch_exception
    @authenticated
    def post(self):
        collection_type = self.get_argument('type')
        relevant_id = self.get_argument('id')
        # TODO: is article or topic visiable ?
        self.muser.update_collection(self.user_id, collection_type, relevant_id)


class MessageHandler(BaseHandler):
    @catch_exception
    @authenticated
    def get(self):
        msg_type = self.get_argument('type')
        page = int(self.get_argument('page', 1))
        size = int(self.get_argument('size', 5))
        msgs = self.muser.get_messages(self.user_id, msg_type, page, size)
        self.write_json(msgs)

    @authenticated
    def post(self):
        """
        Do not post message in here, you should create message after event
        """
        self.write_error(403)


class StarHandler(BaseHandler):
    @catch_exception
    @authenticated
    def get(self):
        star_name = self.get_argument('nickname')
        res = self.muser.is_stared(self.user_id, star_name)
        self.write_result(res)

    @catch_exception
    @authenticated
    def post(self):
        star_name = self.get_argument('nickname')
        self.muser.update_star_user(self.user_id, star_name)

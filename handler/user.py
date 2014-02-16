#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import random
from sys import getsizeof
from tornado.web import authenticated, asynchronous, gen_log
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado import gen
from lib import sendmail
from lib import util
from base import BaseHandler


def login(handler, user_id=None, user=None):
    user = user or handler.get_current_user(user_id)
    handler.session['uid'] = user['uid']
    cnt = handler.muser.get_unread_msg_count(user['uid'])
    user = handler.get_pure_user()
    user['msg_count'] = cnt
    return user

# TODO
class IndexHandler(BaseHandler):
    def get(self):
        # TODO
        self.render('base.html')
        return
        stay_urls = [
            r'/user/(.+)',
            r'/a/browse',
            r'/a/create',
            r'/g/browse',
            r'/g/(\d+)',
            r'/t/(\d+)',
            r'/a/(\d+)',
        ]
        url = self.get_cookie('last_view')
        if url:
            for pattern in stay_urls:
                if re.search(pattern, url):
                    self.redirect(url)
                    return
        self.redirect('/a/browse')


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

    def post(self):
        nickname_or_email = self.get_argument("username")
        password = self.get_argument("password")

        if not util.is_email(nickname_or_email) and util.has_illegal_char(nickname_or_email):
            self.write_errmsg('illegal nickname')
            return
        try:
            user = self.muser.do_login(nickname_or_email, password)
            user = login(self, user=user)
            self.write_json(user)
        except Exception as e:
            self.write_errmsg(e)


class LogoutHandler(BaseHandler):
    def post(self):
        self.session.clear()


class RegisterHandler(BaseHandler):
    def post(self):
        nickname = self.get_arg('nickname')
        password = self.get_arg('password')
        email = self.get_arg('email')

        try:
            self.check_arg('nickname', util.has_illegal_char, result=False)
            self.check_arg('email', util.is_email)
            user_id = self.muser.do_register(nickname, password, email)
            avatar = self.set_random_avatar(nickname)
            self.muser.update_user_info(user_id, avatar=avatar)
            self.send_mail(email, user_id)
            # 前端负责登录
            # user = login(self, user_id=user_id)
            # self.write_json(user)
        except Exception as e:
            self.write_errmsg(e)

    def set_random_avatar(self, nickname):
        avatar_dir = self.settings['avatar_path']
        random_path = os.path.join(avatar_dir, 'random')
        avatar_path = os.path.join(random_path,
                                   random.choice(os.listdir(random_path)))
        with open(avatar_path, 'r') as avatar_fp:
            avatar = util.genavatar(avatar_fp, avatar_dir, nickname)
        if not avatar:
            errmsg = 'set random avatar'
            gen_log.error(errmsg)
            raise Exception(errmsg)
        return avatar

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
    def get(self):
        """
        若成功返回相关信息或1, 失败返回错误信息或0
        """
        try:
            if self.has_argument('activate_account'):
                self.activate_account()
            elif self.has_argument('check_username'):
                self.check_username()
            elif self.has_argument('check_email'):
                self.check_email()
            url = self.get_argument('next')
            if url:
                self.redirect(url)
        except Exception as e:
            self.write_errmsg(e)

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
    @authenticated
    def get(self):
        user = login(self, user=self.current_user)
        self.write_json(user)

    @authenticated
    def post(self):
        """
        用户信息修改, 不处理头像与密码
        """
        self.get_args('nickname', 'email', 'realname',
                      'phone', 'birthday', 'sex',
                      'address', 'intro', 'motto')
        try:
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
        except Exception as e:
            self.write_errmsg(str(e))
            return

    def is_address(self, value):
        # TODO
        return True

    def do_update(self):
        user = self.current_user
        self.muser.update_user_info(user['uid'], **self.args)


# TODO
class AvatarHandler(BaseHandler):
    def init_content(self):
        # max avatar file is 10Mb
        self.max_file_size = 1000000
        pass

    @gen.coroutine
    def set_avatar_from_url(self, url):
        client = AsyncHTTPClient()
        r = yield gen.Task(client.fetch, url)
        result = self.set_avatar(r.body)
        self.write(result)
        self.finish()

    def set_avatar_from_request(self, request):
        if "avatar" in request.files:
            avatar_data = request.files['avatar'][0]['body'],
            result = self.set_avatar(avatar_data)
            self.write(result)
        else:
            self.write('failed')
        self.finish()

    def set_avatar(self, avatar_data, avatar_path=None):
        try:
            filesize = getsizeof(avatar_data)
            if filesize > self.max_file_size:
                return 'exceed'
            with StringIO.StringIO(avatar_data) as avatar_fp:
                avatar_dir = avatar_path or self.settings['avatar_path']
                avatar_name = util.genavatar(avatar_fp,
                                             avatar_dir,
                                             self.penname)
                return avatar_name
        except:
            pass
        return 'failed'

    @asynchronous
    @authenticated
    def post(self):
        self.init_content()
        self.set_avatar_from_request(self.request)


class MemoHandler(BaseHandler):
    @authenticated
    def get(self):
        memo_id = self.get_argument('id')
        try:
            if memo_id:
                memo = self.muser.get_memo(self.user_id, memo_id)
                self.write(memo)
            else:
                page = int(self.get_argument('page', 1))
                size = int(self.get_argument('size', 100))
                memos = self.muser.get_memos(self.user_id, page, size)
                self.write_json(memos)
        except Exception as e:
            self.write_errmsg(e)

    @authenticated
    def post(self):
        try:
            if self.has_argument('create'):
                self.do_create()
            elif self.has_argument('update'):
                self.do_update()
            elif self.has_argument('delete'):
                self.do_delete()
        except Exception as e:
            self.write_errmsg(e)

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
    @authenticated
    def get(self):
        collection_type = self.get_argument('type')
        page = self.get_argument('page', 1)
        size = self.get_argument('size', 5)
        collections = self.muser.get_collections(self.user_id, collection_type, page, size)
        self.write_json(collections)

    @authenticated
    def post(self):
        try:
            collection_type = self.get_argument('type')
            relevant_id = self.get_argument('id')
            self.muser.create_collection(self.user_id, collection_type, relevant_id)
        except Exception as e:
            self.write_errmsg(e)


class MessageHandler(BaseHandler):
    # TODO
    """
    -- wutong 在 test_group 小组提到了你
    -- wutong 评论了你的文章 test_article
    -- wutong 任命你为 test_group 的 leader
    -- 恭喜你获得了 article_master 成就
    -- 恭喜你获得了 king_of_stupid 头衔
    """
    @authenticated
    def get(self):
        msg_type = self.get_argument('type')
        page = self.get_argument('page', 1)
        size = self.get_argument('size', 5)
        msgs = self.muser.get_messages(self.user_id, msg_type, page, size)
        self.write_json(msgs)

    @authenticated
    def post(self):
        """
        Do not post message in here, you should create message after event
        """
        self.write_error(403)

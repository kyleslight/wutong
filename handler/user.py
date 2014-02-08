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


def login(self, user_id=None, user=None):
    """
    `self` is `BaseHandler` object
    """
    user = user or self.get_current_user(user_id)
    self.session['uid'] = user['uid']
    cnt = self.muser.get_unread_msg_count(user['uid'])
    user = self.get_pure_user()
    user['msg_count'] = cnt
    self.write_json(user)

# TODO
class IndexHandler(BaseHandler):
    """
    -- 'wutong'::url 回复了你的话题 'test_topic'::url
    -- wutong 在 test_group 小组提到了你
    -- wutong 评论了你的文章 test_article
    -- wutong 任命你为 test_group 的 leader
    -- 恭喜你获得了 article_master 成就
    -- 恭喜你获得了 king_of_stupid 头衔
    """
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
            self.write_errmsg('illegal username')
            return
        user = self.muser.do_login(nickname_or_email, password)
        if user:
            login(self, user=user)
        else:
            self.write_errmsg('password or account error')


class LogoutHandler(BaseHandler):
    def post(self):
        self.session.clear()


class RegisterHandler(BaseHandler):
    def post(self):
        nickname = self.get_argument('nickname')
        password = self.get_argument('password')
        email = self.get_argument('email')

        if util.has_illegal_char(nickname):
            self.write_errmsg('invalid nickname')
            return
        if not util.is_email(email):
            self.write_errmsg('invalid email')
            return
        value = self.muser.do_register(nickname, password, email)
        if self.register_error(value):
            return

        user_id = value
        try:
            avatar = self.set_random_avatar(nickname)
            self.muser.update_user_info(user_id, avatar=avatar)
            self.send_mail(email, user_id)
            # 前端负责登录
            # login(self, user_id=user_id)
        except Exception as e:
            gen_log.error(e)


    def register_error(self, value):
        if value == -1:
            self.write_errmsg('nickname exists')
        elif value == -2:
            self.write_errmsg('email exists')
        else:
            return False
        return True

    def set_random_avatar(self, nickname):
        avatar_dir = self.settings['avatar_path']
        random_path = os.path.join(avatar_dir, 'random')
        avatar_path = os.path.join(random_path,
                                   random.choice(os.listdir(random_path)))
        with open(avatar_path, 'r') as avatar_fp:
            avatar = util.genavatar(avatar_fp, avatar_dir, nickname)
        if not avatar:
            gen_log.error('set random avatar')
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
            gen_log.error("send email to '%s' error" % email)


class AccountHandler(BaseHandler):
    def get(self):
        """
        若成功返回相关信息或1, 失败返回错误信息或0
        """
        args = self.request.arguments
        if 'activate_account' in args:
            self.activate_account()
        elif 'check_username' in args:
            self.check_username()
        elif 'check_email' in args:
            self.check_email()
        url = self.get_argument('next')
        if url:
            self.redirect(url)

    def activate_account(self):
        value = self.get_argument('v')
        user_id = util.decrypt(value)
        if self.muser.do_activate_account(user_id):
            login(self, user_id=user_id)
        else:
            self.write_errmsg('activate account failed')

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
        login(self, user=self.current_user)

    @authenticated
    def post(self):
        """
        用户信息修改, 不处理头像与密码
        """
        self.info = self.get_update_account_info()
        if self.info is None:
            return
        self.add_update_info('realname')
        self.add_update_info('phone')
        self.add_update_info('sex')
        self.add_update_info('birthday')
        self.add_update_info('address')
        self.add_update_info('intro')
        self.add_update_info('motto')
        self.do_check()
        self.do_update()

    def get_update_account_info(self):
        kwargs = self.request.arguments
        info = {}
        if 'nickname' in kwargs:
            nickname = self.get_argument('nickname')
            if self.muser.is_nickname_exist(nickname):
                self.write_errmsg('nickname exist')
                return None
            else:
                info['nickname'] = nickname
        if 'email' in kwargs:
            email = self.get_argument('email')
            if self.muser.is_email_exist(email):
                self.write_errmsg('email exist')
                return None
            else:
                info['email'] = email
        return info

    def add_update_info(self, key):
        value = self.get_argument(key)
        if value:
            self.info[key] = value

    def do_check(self):
        if self._check_key('nickname', util.has_illegal_char) is True:
            self.write_errmsg('invalid nickname')
            return
        if self._check_key('email', util.is_email) is False:
            self.write_errmsg('invalid email')
            return
        if self._check_key('phone', util.is_phone) is False:
            self.write_errmsg('invalid phone')
            return
        if self._check_key('birthday', util.is_time) is False:
            self.write_errmsg('invalid time')
            return
        if self._check_key('realname', util.has_illegal_char) is True:
            self.write_errmsg('invalid realname')
            return
        if self._check_key('sex', lambda s: s in ('true', 'false')) is False:
            self.write_errmsg('invalid sex')
            return
        # if not self._check_key('address', lambda s: s):
        #     self.write_errmsg('invalid address')
        #     return

    def do_update(self):
        user = self.current_user
        if not self.muser.update_user_info(user['uid'], **self.info):
            self.write_errmsg('unknown error')

    def _check_key(self, key, callback):
        value = self.info.get(key)
        if value:
            return callback(value)
        return None


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
        if memo_id:
            memo = self.muser.get_memo(self.user_id, memo_id)
            if memo:
                self.write_json(memo)
            else:
                self.write_error(403)
        else:
            page = self.get_argument('page', 1)
            size = self.get_argument('size', 100)
            memos = self.muser.get_memos(self.user_id, page, size)
            self.write_json(memos)

    @authenticated
    def post(self):
        args = self.request.arguments
        if 'create' in args:
            self.do_create()
        elif 'update' in args:
            self.do_update()
        elif 'delete' in args:
            self.do_delete()

    def get_update_title_and_content(self):
        title = self.get_argument('title')
        content = self.get_argument('content')

        if not title and content:
            title = content[:10]
            if len(content) > 10:
                title += u'...'
        return title, content

    def do_create(self):
        title, content = self.get_update_title_and_content()
        if not title and not content:
            self.write_errmsg('empty input')
            return
        memo = self.muser.create_memo(self.user_id, title, content)
        self.write(memo)

    def do_update(self):
        title, content = self.get_update_title_and_content()
        if not title and not content:
            self.write_errmsg('empty input')
            return
        memo_id = self.get_argument('id')
        memo = self.muser.update_memo(self.user_id, memo_id, title, content)
        if memo:
            self.write(memo)
        else:
            self.write_errmsg('update memo failed')

    def do_delete(self):
        memo_id = self.get_argument('id')
        if not self.muser.delete_memo(self.user_id, memo_id):
            self.write_errmsg('delete memo failed')


# TODO
class CollectionHandler(BaseHandler):
    def add_collection(self, article_id):
        return self.create_article_collection(self.user_id, article_id)

    def get_collections(self, page):
        return self.muser.get_collections(self.user_id, page)

    @authenticated
    def get(self):
        page = self.get_argument('page', 1)
        collections = self.get_collections(page)
        self.write(json_encode(collections))

    @authenticated
    def post(self):
        article_id = self.get_argument('article_id')
        self.write(self.add_collection(article_id))


# TODO
class AutoCompletionHandler(BaseHandler):
    def get(self):
        query = self.get_argument('q')

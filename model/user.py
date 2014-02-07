#!/usr/bin/env python
# -*- coding: utf-8 -*-


class UserModel(object):
    def __init__(self, db):
        self.db = db

    def get_uid(self, nickname_or_email):
        return self.db.callfirstfield('get_uid', nickname_or_email)

    def is_nickname_exist(self, nickname):
        uid = self.get_uid(nickname)
        return uid is not None

    def is_email_exist(self, email):
        uid = self.get_uid(email)
        return uid is not None

    def do_register(self, nickname, password, email):
        return self.db.callfirstfield('do_user_register', nickname, password, email)

    def do_activate_account(self, uid):
        uid = self.db.callfirstfield('do_user_activate', uid)
        return uid > 0

    def do_login(self, nickname_or_email, password):
        """
        return `user` if success else None
        """
        return self.db.calljson('do_user_login', nickname_or_email, password)

    def get_user(self, uid):
        return self.db.calljson('get_user', uid)

    def update_user_info(self, uid, **kwargs):
        return self.db.update('myuser', kwargs, where='uid=%s', wherevalues=[uid])

    def get_user_homepage(self, nickname):
        return self.db.calljson('get_user_homepage', nickname)

    def create_memo(self, uid, title, content):
        memo = self.db.calljson('create_user_memo', uid, title, content)
        if memo:
            memo.pop('uid')
        return memo

    def get_memo(self, uid, memo_id):
        memo = self.db.calljson('get_user_memo', uid, memo_id)
        if memo:
            memo.pop('uid')
        return memo

    def get_memos(self, uid, page, size):
        limit = size
        offset = (page - 1) * size
        return self.db.calljson('get_user_memos', uid, limit, offset)

    def update_memo(self, uid, memo_id, title, content):
        return self.db.calljson('update_user_memo', uid, memo_id, title, content)

    def delete_memo(self, uid, memo_id):
        return self.db.delete('user_memo', where='uid=%s and id=%s', wherevalues=[uid, memo_id])

    def get_unread_msg_count(self, uid):
        map_table = {
            '1': 'reply',
            '2': 'push',
        }
        cnt = self.db.calljson('get_user_unread_msg_count', uid)
        tmp = {}
        for item in cnt:
            key = map_table[item['type']]
            tmp[key] = item['sum']
        return tmp

    def get_collections(self, uid, page, size):
        limit = size
        offset = (page - 1) * size
        return self.db.calljson('get_user_memos', uid, limit, offset)

    # def create_collection(self, uid, aid):
    #     select = 'SELECT create_article_collection(%s, %s)'
    #     return self.db.getfirstfield(select, uid, aid)

    # def get_user_groups(self, uid, limit=5, offset=0):
    #     select = 'SELECT get_user_groups(%s, %s, %s)'
    #     return self.db.getjson(select, uid, limit, offset)

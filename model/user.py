#!/usr/bin/env python
# -*- coding: utf-8 -*-


class UserModel(object):
    def __init__(self, db):
        self.db = db

    def get_uid(self, nickname_or_email):
        uid = self.db.callfirstfield('get_uid', nickname_or_email)
        return uid

    def is_nickname_exist(self, nickname):
        uid = self.get_uid(nickname)
        return uid is not None

    def is_email_exist(self, email):
        uid = self.get_uid(email)
        return uid is not None

    def do_register(self, nickname, password, email):
        value = self.db.callfirstfield('do_user_register', nickname, password, email)
        if value > 0:
            return value
        elif value == -1:
            raise Exception('nickname exist')
        elif value == -2:
            raise Exception('email exist')

    def do_activate_account(self, uid):
        uid = self.db.callfirstfield('do_user_activate', uid)
        if uid > 0:
            return uid
        else:
            raise Exception('activate failed')

    def do_login(self, nickname_or_email, password):
        """
        return `user` if success else None
        """
        user = self.db.calljson('do_user_login', nickname_or_email, password)
        if not user:
            raise Exception('user not exist or password error')
        return user

    def get_user(self, uid):
        return self.db.calljson('get_user', uid)

    def update_user_info(self, uid, **kwargs):
        if not self.db.update('myuser', kwargs, where='uid=%s', wherevalues=[uid]):
            raise Exception('update user failed')

    def get_user_homepage(self, nickname):
        return self.db.calljson('get_user_homepage', nickname)

    def create_memo(self, uid, title, content):
        memo = self.db.calljson('create_user_memo', uid, title, content)
        if not memo:
            raise Exception('create memo failed')
        return memo

    def get_memo(self, uid, memo_id):
        memo = self.db.calljson('get_user_memo', uid, memo_id)
        if not memo:
            raise Exception('memo not exist')
        return memo

    def get_memos(self, uid, page, size):
        limit = size
        offset = (page - 1) * size
        memos = self.db.calljson('get_user_memos', uid, limit, offset)
        if not memos:
            raise Exception('memos not exist')
        return memos

    def update_memo(self, uid, memo_id, title, content):
        memo = self.db.calljson('update_user_memo', uid, memo_id, title, content)
        if not memo:
            raise Exception('update memo failed')
        return memo

    def delete_memo(self, uid, memo_id):
        res = self.db.delete('user_memo', where='uid=%s and id=%s', wherevalues=[uid, memo_id])
        if not res:
            raise Exception('delete memo failed')

    def update_collection(self, uid, collection_type, relevant_id):
        res = self.db.call('update_user_collection', uid, collection_type, relevant_id)
        if not res:
            raise Exception('update collection failed')

    def get_collections(self, uid, collection_type, page, size):
        """
        `collection_type` must in ('1', '2')
        """
        limit = size
        offset = (page - 1) * limit
        return self.db.calljson('get_user_collections', uid, collection_type, limit, offset)

    def get_messages(self, uid, msg_type, page, size):
        limit = size
        offset = (page - 1) * limit
        return self.db.calljson('get_user_msgs', uid, msg_type, limit, offset)

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

    def get_mygroups(self, uid, page, size):
        limit = size
        offset = (page - 1) * limit
        return self.db.calljson('get_mygroups', uid, limit, offset)

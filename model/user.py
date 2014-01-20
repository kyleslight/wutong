#!/usr/bin/env python
# -*- coding: utf-8 -*-


class UserModel(object):
    def __init__(self, db):
        self.db = db

    def get_uid(self, account):
        select = 'SELECT get_uid(%s)'
        uid = self.db.getfirstfield(select, account)
        return uid

    def get_user_permission(self, uid):
        select = 'SELECT get_user_permission(%s)'
        user_pms = self.db.getjson(select, uid)
        return user_pms

    def get_user_info(self, uid):
        select = 'SELECT get_user_info(%s)'
        user_info = self.db.getjson(select, uid)
        return user_info

    def is_user_exists(self, email=None, penname=None, phone=None):
        select = 'SELECT is_user_exists(%s, %s, %s)'
        uid = self.db.getfirstfield(select, email, penname, phone)
        return uid

    def do_register(self, email, penname, password):
        select = 'SELECT do_register_user(%s, %s, %s)'
        hashuid = self.db.getfirstfield(select, email, penname, password)
        return hashuid

    def do_activate(self, hashuid):
        select = 'SELECT do_activate_user(%s)'
        uid = self.db.getfirstfield(select, hashuid)
        return uid

    def do_login(self, account, password):
        select = 'SELECT do_login_user(%s, %s)'
        uid = self.db.getfirstfield(select, account, password)
        return uid

    def update_user_avatar_by_penname(self, penname, avatar_url):
        update = 'UPDATE "user" SET avatar = %s WHERE penname = %s'
        res = self.db.execute(update, avatar_url, penname)
        return res

    def update_user_info(self, uid, **kwargs):
        args = [
            kwargs['email'],
            kwargs['penname'],
            kwargs['phone'],
            kwargs.get('realname'),
            kwargs.get('sex'),
            kwargs.get('age'),
            kwargs.get('address'),
            kwargs.get('intro'),
            kwargs.get('motto'),
            kwargs.get('avatar'),
        ]

        select = '''SELECT update_user_info(
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        res = self.db.execute(select, uid, *args)
        return res

    def create_memo(self, uid, title, content):
        insert = '''insert into memo
                           (uid, title, content)
                    values (%s, %s, %s)
                    returning id'''
        memo_id = self.db.getfirstfield(insert, uid, title, content)
        return memo_id

    def get_memo(self, memo_id):
        select = '''SELECT row_to_json(j.*)
                      FROM (
                            SELECT *
                              FROM memo
                             WHERE id = %s
                        ) j'''
        memo = self.db.getjson(select, memo_id)
        return memo

    def get_memos(self, uid, limit, offset):
        select = '''SELECT array_to_json(array_agg(aj))
                      FROM (
                            SELECT *
                              FROM memo
                             WHERE uid = %s
                             LIMIT %s
                            OFFSET %s
                        ) aj'''
        memos = self.db.getjson(select, uid, limit, offset)
        return memos

    def update_memo(self, uid, memo_id, title, content):
        update = '''update memo
                       set title = %s,
                           content = %s
                     where id = %s
                       and uid = %s'''
        return self.db.execute(update, title, content, memo_id, uid)

    def delete_memo(self, uid, memo_id):
        delete = 'delete from memo where id = %s and uid = %s'
        return self.db.execute(delete, memo_id, uid)

    def get_collections(self, uid, limit=5, offset=0):
        select = 'SELECT get_article_collections(%s, %s, %s)'
        return self.db.getjson(select, uid, limit, offset)

    def create_collection(self, uid, aid):
        select = 'SELECT create_article_collection(%s, %s)'
        return self.db.getfirstfield(select, uid, aid)

    def get_user_groups(self, uid, limit=5, offset=0):
        select = 'SELECT get_user_groups(%s, %s, %s)'
        return self.db.getjson(select, uid, limit, offset)

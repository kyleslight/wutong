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
            kwargs.get('motton'),
            kwargs.get('avatar'),
        ]

        select = '''SELECT update_user_info(
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        res = self.db.execute(select, uid, *args)
        return res

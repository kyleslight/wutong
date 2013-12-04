#!/usr/bin/env python
# -*- coding: utf-8 -*-

class UserModel:

    def __init__(self, db):
        self.db = db

    def get_uid(self, account):
        select = 'SELECT get_uid(%s)'
        uid = self.db.getfirstfield(select, account)
        return uid

    def get_user_info(self, uid):
        select = 'SELECT get_user_info(%s)'
        user_info = self.db.getjson(select, uid)
        return user_info

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

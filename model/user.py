#!/usr/bin/env python
# -*- coding: utf-8 -*-

class UserModel:
    '''account指 email或penname或phone'''
    def __init__(self, db):
        self.db = db

    def do_register(self, email, password, penname):
        select = 'SELECT f_register_user(%s, %s, %s)'
        hashuid = self.db.getfirstfield(select, email, penname, password)
        return hashuid

    def do_activate_by_hashuid(self, hashuid):
        select = 'SELECT f_activate_user(%s)'
        uid = self.db.getfirstfield(select, hashuid)
        return uid

    def do_login_by_account_and_password(self, account, password):
        select = 'SELECT f_user_login(%s, %s)'
        uid = self.db.getfirstfield(select, account, password)
        return uid

    def get_user_info_by_uid(self, uid):
        select = 'SELECT f_get_user_info_j(%s)'
        user_info = self.db.getfirstfield(select, uid)
        return user_info

    def get_score_by_uid(self, uid):
        return 0

    def get_uid_by_account(self, account):
        select = 'SELECT f_get_uid(%s)'
        uid = self.db.getfirstfield(select, account)
        return uid


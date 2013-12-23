#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import util
from model.user import UserModel


class UserModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = util.db_test
        cls.tearDownClass()

        cls.model = UserModel(util.db_test)
        cls.email = 'test@email.com'
        cls.penname = 'test'
        cls.password = 'test'

        sql = '''insert into "user"
                        (email, penname, password)
                 values (%s, %s, crypt(%s, gen_salt('bf')))
                 returning uid,
                           md5(CAST(uid AS varchar)) AS "hashuid"'''
        row = cls.db.getrow(sql, cls.email, cls.penname, cls.password)
        cls.uid = row[0]
        cls.hashuid = row[1]

    @classmethod
    def tearDownClass(cls):
        cls.db.execute('delete from "user"')

    def test_get_uid(self):
        uid = self.model.get_uid(self.email)
        self.assertIsInstance(uid, int)

    def test_get_user_permission(self):
        perm = self.model.get_user_permission(self.uid)
        assert(perm)

    def test_get_user_info(self):
        info = self.model.get_user_info(self.uid)
        assert(info)

    def test_do_register(self):
        hashuid = self.model.do_register('register@email.com',
                                         'register_test',
                                         'register_test')
        assert(hashuid)
        self.db.execute("""delete from "user"
                            where md5(cast(uid as varchar)) = %s""",
                        hashuid)

    def test_do_activate(self):
        uid = self.model.do_activate(self.hashuid)
        assert(uid)

    def test_do_login(self):
        uid = self.model.do_login(self.email, self.password)
        self.assertIsInstance(uid, int)

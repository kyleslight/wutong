#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from db import Pool
import user
import group

# TODO: 异常测试
class TestModel(unittest.TestCase):

    def setUp(self):
        self.dsn = "host=%s dbname=%s user=%s password=%s" % (
                        "localhost", "wutong_test", "wutong", "wutong"
                    )
        self.db = Pool.instance(self.dsn)
        self.execute = self.db._get_connection()._execute

        self.email = "test@wutong.com"
        self.penname = "wutong"
        self.password = "wutong"
        self.user_intro = "user_intro"
        self.user_motton = "user_motton"
        self.group_name = "group_name"
        self.group_intro = "group_intro"
        self.group_motton = "group_motton"

    def tearDown(self):
        # self.execute('DELETE FROM "user" *')
        # self.execute('DELETE FROM "group" *')
        pass

    def test_db(self):
        dirpath = "../dbschema/"

        self.assertEqual(self.db.getfirstfield('SELECT 1'), 1)
        self.assertEqual(self.db.getjson("SELECT '1'"), 1)
        self.assertIsNotNone(self.db.getitem('SELECT 1'))
        self.assertIsNotNone(self.db.getitems('SELECT 1'))
        sql = open(dirpath + "schema.sql", "r").read()
        self.assertTrue(self.execute(sql))
        sql = open(dirpath + "function.sql", "r").read()
        self.assertTrue(self.execute(sql))

    def test_user(self):
        model = user.UserModel(self.db)

        hashuid = model.do_register(email=self.email, penname=self.penname, password=self.password)
        self.assertIsNotNone(hashuid)
        uid = model.do_activate_by_hashuid(hashuid)
        self.assertIsInstance(uid, int)
        self.assertIsInstance(model.get_uid_by_account(self.penname), int)
        self.assertIsInstance(model.do_login_by_account_and_password(account=self.email, password=self.password), int)
        self.assertIsNotNone(model.get_user_info_by_uid(uid))
        self.assertIsInstance(model.get_score_by_uid(uid), (int, float))

    def test_group(self):
        pass


if __name__ == "__main__":
    unittest.main()

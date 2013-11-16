#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from db import Pool
from user import UserModel
from group import GroupModel

# TODO: 异常测试
class TestModel(unittest.TestCase):

    def setUp(self):
        self.dsn = "host=%s dbname=%s user=%s password=%s" % (
            "localhost", "wutong_test", "wutong", "wutong"
        )
        self.db = Pool.instance(self.dsn)

        self.user = {
            "email": "test@wutong.com",
            "penname": "wutong",
            "password": "wutong",
            "realname": "wu xiao tong",
            "sex": True, # man
            "intro": "intro",
            "motton": "motton",
            "avatar": "/image/test.png",
        }
        self.group = {
            "name": "testgroup",
            "founder": self.user["penname"],
            "intro": "intro",
            "motton": "motton",
            "publicity": True,
        }
        self.message = {
            "content": "content",
            "title": "title",
            "reply_id": 1,
        }

        self.do_test_db()

    def tearDown(self):
        pass

    def do_test_db(self):
        dirpath = "../dbschema/"

        self.assertEqual(self.db.getfirstfield('SELECT 1'), 1)
        self.assertEqual(self.db.getjson("SELECT '1'"), 1)
        self.assertEqual(self.db.getitem('SELECT 1'), (1,))
        self.assertEqual(self.db.getitems('SELECT 1'), [(1,)])
        sql = open(dirpath + "schema.sql", "r").read()
        self.assertTrue(self.db.execute(sql))
        sql = open(dirpath + "function.sql", "r").read()
        self.assertTrue(self.db.execute(sql))

class TestUserModel(TestModel):

    def setUp(self):
        super(TestUserModel, self).setUp()
        self.db.execute('DELETE FROM "user" *')
        self.model = UserModel(self.db)

    def test(self):
        hashuid = self.model.do_register(
                email=self.user["email"],
                penname=self.user["penname"],
                password=self.user["password"]
            )
        self.assertIsNotNone(hashuid)
        uid = self.model.do_activate_by_hashuid(hashuid)
        self.assertIsInstance(uid, int)
        uid = self.model.get_uid_by_account(self.user["penname"])
        self.assertIsInstance(uid, int)
        uid = self.model.do_login_by_account_and_password(
                account=self.user["email"],
                password=self.user["password"]
            )
        self.assertIsInstance(uid, int)
        user_info = self.model.get_user_info_by_uid(uid)
        self.assertIsNotNone(user_info)
        score = self.model.get_score_by_uid(uid)
        self.assertIsInstance(score, (int, float))

class TestGroupModel(TestModel):

    def setUp(self):
        super(TestGroupModel, self).setUp()
        self.db.execute('DELETE FROM "user" *')
        self.db.execute('DELETE FROM "group" *')
        self.model = GroupModel(self.db)
        usermodel = UserModel(self.db)
        hashuid = usermodel.do_register(
                email=self.user["email"],
                penname=self.user["penname"],
                password=self.user["password"]
            )
        self.uid = usermodel.do_activate_by_hashuid(hashuid)

    def test(self):
        gid = self.model.do_create(
                name=self.group["name"],
                founder=self.user["penname"],
                intro=self.group["intro"],
                motton=self.group["motton"]
            )
        self.assertIsInstance(gid, int)
        res = self.model.do_user_join_group(gid=gid, uid=self.uid)
        self.assertTrue(res)
        for i in xrange(70):
            mid = self.model.do_insert_message(
                    gid=gid,
                    uid=self.uid,
                    content=self.message["content"],
                    title=self.message["title"]
                )
            self.assertIsInstance(mid, int)
            bid = self.model.do_insert_bulletin(
                    gid=gid,
                    uid=self.uid,
                    content=self.message["content"],
                    title=self.message["title"]
                )
            self.assertIsInstance(bid, int)

        msg = self.model.get_group_message(mid)
        self.assertIsNotNone(msg)
        msgs = self.model.get_group_messages(gid, 30, 0)
        self.assertIsInstance(msgs, list)
        mem = self.model.get_member_info(gid, self.uid)
        self.assertIsNotNone(mem)
        buls = self.model.get_group_bulletins(gid, 6, 0)
        self.assertIsInstance(buls, list)
        self.model.update_group_info(
                gid,
                founder=self.group["founder"],
                name=self.group["name"]+"update",
                intro=self.group["intro"]+"update",
                motton=self.group["motton"]+"update"
            )

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestUserModel("test"))
    suite.addTest(TestGroupModel("test"))
    return suite

def main():
    runner = unittest.TextTestRunner()
    runner.run(suite())

if __name__ == "__main__":
    main()

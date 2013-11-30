#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util import path
import unittest
from model.db import Pool
from model.user import UserModel
from model.group import GroupModel

# TODO: 异常测试
class TestModelBase(unittest.TestCase):

    def setUp(self):
        self.dsn = "host=%s dbname=%s user=%s password=%s" % (
            "localhost", "wutong_test", "wutong", "wutong"
        )
        self.db = Pool.instance(self.dsn)

        self.users = [
            {
                "email": "user1@wutong.com",
                "penname": "wutong",
                "password": "wutong",
                "realname": "wu xiao tong",
                "sex": True, # man
                "intro": "intro1",
                "motton": "motton1",
                "avatar": "/image/user1.png",
            },
            {
                "email": "user2@wutong.com",
                "penname": "user2",
                "password": "user2",
                "realname": "wu er tong",
                "sex": False, # man
                "intro": "intro2",
                "motton": "motton2",
                "avatar": "/image/user2.png",
            },
        ]
        self.groups = [
            {
                "name": "group1",
                "founder": self.users[0]["penname"],
                "intro": "intro1",
                "motton": "motton1",
                "publicity": True,
            },
            {
                "name": "group2",
                "founder": self.users[1]["penname"],
                "intro": "intro2",
                "motton": "motton2",
                "publicity": False,
            },
        ]
        self.bulletin = {
            "content": "bulletin content",
            "title": "bulletin title",
        }
        self.topic = {
            "content": "topic content",
            "title": "topic title",
        }
        self.message = {
            "content": "message content",
            "reply_id": 1,
        }


class TestDBModel(TestModelBase):
    def test(self):
        self.assertEqual(self.db.getfirstfield('SELECT 1'), 1)
        self.assertEqual(self.db.getjson("SELECT '1'"), 1)
        self.assertEqual(self.db.getitem('SELECT 1'), (1,))
        self.assertEqual(self.db.getitems('SELECT 1'), [(1,)])
        dirpath = path("model/dbschema/")
        sql = open(dirpath + "schema.sql", "r").read()
        self.assertTrue(self.db.execute(sql))
        sql = open(dirpath + "function.sql", "r").read()
        self.assertTrue(self.db.execute(sql))
        self.db.execute('DELETE FROM "group_user" *')
        self.db.execute('DELETE FROM "group_topic" *')
        self.db.execute('DELETE FROM "group_message" *')
        self.db.execute('DELETE FROM "group" *')
        self.db.execute('DELETE FROM "user" *')


class TestUserModel(TestModelBase):

    def setUp(self):
        super(TestUserModel, self).setUp()
        self.model = UserModel(self.db)
        self.db.execute('DELETE FROM "user" *')

    def test(self):
        for user in self.users:
            hashuid = self.model.do_register(
                    email=user["email"],
                    penname=user["penname"],
                    password=user["password"]
                )
            self.assertIsNotNone(hashuid)
            uid = self.model.do_activate_by_hashuid(hashuid)
            self.assertIsInstance(uid, int)
            uid = self.model.get_uid_by_account(user["penname"])
            self.assertIsInstance(uid, int)
            uid = self.model.do_login_by_account_and_password(
                    account=user["email"],
                    password=user["password"]
                )
            self.assertIsInstance(uid, int)
            user_info = self.model.get_user_info_by_uid(uid)
            self.assertIsNotNone(user_info)
            score = self.model.get_score_by_uid(uid)
            self.assertIsInstance(score, (int, float))

    def tearDown(self):
        self.db.execute('DELETE FROM "user" *')


class TestGroupModel(TestModelBase):

    def setUp(self):
        super(TestGroupModel, self).setUp()
        self.db.execute('DELETE FROM "group" *')
        self.model = GroupModel(self.db)
        usermodel = UserModel(self.db)
        user = self.users[0]
        hashuid = usermodel.do_register(
                email=user["email"],
                penname=user["penname"],
                password=user["password"]
            )
        self.uid = usermodel.do_activate_by_hashuid(hashuid)
        self.assertIsInstance(self.uid, int)
        self.founder = user["penname"]

    def test(self):
        for group in self.groups:
            gid = self.model.do_create(
                    name=group["name"],
                    founder=group["founder"],
                    intro=group["intro"],
                    motton=group["motton"]
                )
            self.assertIsInstance(gid, int)
            res = self.model.do_user_join_group(gid=gid, uid=self.uid)
            self.assertTrue(res)

        # TODO: delete this
        gid = 1
        for i in xrange(7):
            tid = self.model.do_insert_topic(
                    gid=gid,
                    uid=self.uid,
                    content=self.topic["content"],
                    title=self.topic["title"],
                )
            mid = self.model.do_insert_message(
                    gid=gid,
                    uid=self.uid,
                    content=self.message["content"],
                    reply_id=tid
                )
            self.assertIsInstance(mid, int)
            bid = self.model.do_insert_bulletin(
                    gid=gid,
                    uid=self.uid,
                    content=self.bulletin["content"],
                    title=self.bulletin["title"]
                )
            self.assertIsInstance(bid, int)

        for i in xrange(30):
            mid = self.model.do_insert_message(
                    gid=gid,
                    uid=self.uid,
                    content=self.message["content"],
                )
            self.assertIsInstance(mid, int)

        msg = self.model.get_group_message(mid)
        self.assertIsNotNone(msg)
        msgs = self.model.get_group_messages(gid, 30, 0)
        self.assertIsInstance(msgs, list)
        tpc = self.model.get_group_topic(tid)
        self.assertIsNotNone(tpc)
        tpcs = self.model.get_group_topics(gid, 30, 0)
        self.assertIsInstance(tpcs, list)
        mem = self.model.get_member_info(gid, self.uid)
        self.assertIsNotNone(mem)
        buls = self.model.get_group_bulletins(gid, 6, 0)
        self.assertIsInstance(buls, list)
        for group in self.groups:
            self.model.update_group_info(
                    gid,
                    founder=group["founder"],
                    name=group["name"]+"update",
                    intro=group["intro"]+"update",
                    motton=group["motton"]+"update"
                )

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestDBModel("test"))
    suite.addTest(TestUserModel("test"))
    suite.addTest(TestGroupModel("test"))
    return suite

def main():
    runner = unittest.TextTestRunner()
    runner.run(suite())

if __name__ == "__main__":
    main()

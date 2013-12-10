#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util import path, is_debug
import unittest
from model.db import Pool
from model.user import UserModel
from model.group import GroupModel


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
                "realname": u"吴大桐",
                "sex": u"男",
                "intro": "intro1",
                "motton": "motton1",
                "avatar": "/image/user1.png",
            },
            {
                "email": "user2@wutong.com",
                "penname": "user2",
                "password": "user2",
                "realname": u"吴小桐",
                "sex": u"女",
                "intro": "intro2",
                "motton": "motton2",
                "avatar": "/image/user2.png",
            },
        ]
        self.groups = [
            {
                "name": "group1",
                "intro": "intro1",
                "motton": "motton1",
                "is_public": True,
            },
            {
                "name": "group2",
                "intro": "intro2",
                "motton": "motton2",
                "is_public": False,
            },
        ]
        self.bulletin = {
            "title": "bulletin title",
            "content": "bulletin content",
        }
        self.topic = {
            "title": "topic title",
            "content": "topic content",
        }
        self.message = {
            "content": "message content",
            "reply_id": 1,
        }


class TestDBModel(TestModelBase):

    def test(self):
        self.assertEqual(self.db.getfirstfield('SELECT 1'), 1)
        self.assertEqual(self.db.getjson("SELECT '1'"), 1)
        self.assertEqual(self.db.getrow('SELECT 1'), (1,))
        self.assertEqual(self.db.getrows('SELECT 1'), [(1,)])
        dirpath = path("model/dbschema/")
        sql = open(dirpath + "schema.sql", "r").read()
        self.assertTrue(self.db.execute(sql))


class TestUserModel(TestModelBase):

    def setUp(self):
        super(TestUserModel, self).setUp()
        self.model = UserModel(self.db)
        self.db.execute('DELETE FROM "user" *')

    def tearDown(self):
        if is_debug():
            return
        self.db.execute('DELETE FROM "user" *')

    def test(self):
        user = self.users[1]
        hashuid = self.model.do_register(
                email=user["email"],
                penname=user["penname"],
                password=user["password"]
            )
        self.assertIsInstance(hashuid, basestring)
        uid = self.model.do_activate(hashuid)
        self.assertIsInstance(uid, int)
        uid = self.model.get_uid(user["penname"])
        self.assertIsInstance(uid, int)
        uid = self.model.do_login(
                account=user["email"],
                password=user["password"]
            )
        self.assertIsInstance(uid, int)
        user_info = self.model.get_user_info(uid)
        self.assertIsNotNone(user_info)


class TestGroupModel(TestModelBase):

    def setUp(self):
        super(TestGroupModel, self).setUp()
        self.model = GroupModel(self.db)
        usermodel = UserModel(self.db)
        self.db.execute('DELETE FROM "user" *')
        self.db.execute('DELETE FROM "group" *')

        self.uids = []
        for user in self.users:
            hashuid = usermodel.do_register(
                    email=user["email"],
                    penname=user["penname"],
                    password=user["password"]
                )
            uid = usermodel.do_activate(hashuid)
            self.uids.append(usermodel.get_uid(user["email"]))

        self.assertIsInstance(self.uids[0], int)

    def tearDown(self):
        if is_debug():
            return
        self.db.execute('DELETE FROM "user" *')
        self.db.execute('DELETE FROM "group" *')

    def test(self):
        uid = self.uids[0]
        for group in self.groups:
            gid = self.model.do_create(
                    uid=uid,
                    name=group["name"],
                    intro=group["intro"],
                    motton=group["motton"],
                    is_public=group["is_public"]
                )
            self.assertIsInstance(gid, int)
        res = self.model.do_join_group(gid=gid, uid=self.uids[1])
        self.assertTrue(res)

        gid = 1
        for i in xrange(7):
            tid = self.model.do_create_topic(
                    gid=gid,
                    uid=uid,
                    title=self.topic["title"],
                    content=self.topic["content"]
                )
            self.assertIsInstance(tid, int)
            id = self.model.do_create_chat(
                    gid=gid,
                    uid=uid,
                    content=self.message["content"],
                    reply_id=tid
                )
            self.assertIsInstance(id, int)
            bid = self.model.do_create_bulletin(
                    gid=gid,
                    uid=uid,
                    content=self.bulletin["content"],
                    title=self.bulletin["title"]
                )
            self.assertIsInstance(bid, int)

        for i in xrange(30):
            mid = self.model.do_create_chat(
                    gid=gid,
                    uid=uid,
                    content=self.message["content"]
                )
            self.assertIsInstance(mid, int)

        chats = self.model.get_chats(gid, 30, 0)
        self.assertIsInstance(chats, list)
        tpc = self.model.get_topic(tid)
        self.assertIsInstance(tpc, dict)
        tpcs = self.model.get_topics(gid, 30, 0)
        self.assertIsInstance(tpcs, list)
        mem = self.model.get_member_info(gid, uid)
        self.assertIsInstance(mem, dict)
        buls = self.model.get_bulletins(gid, 6, 0)
        self.assertIsInstance(buls, list)


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

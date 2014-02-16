#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import util
from model.group import GroupModel


class GroupModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = util.db_test
        cls.tearDownClass()

        cls.uid = cls.db.getfirstfield("""
            insert into "user"
                   (email, penname, password, is_activated)
            values ('test@email.com', 'test', 'test', true)
            returning uid
        """)

        cls.model = GroupModel(util.db_test)
        cls.name = 'test_group'

        sql = """insert into "group"
                        (uid, name)
                 values (%s, %s)
                 returning gid"""
        cls.gid = cls.db.getfirstfield(sql, cls.uid, cls.name)

    @classmethod
    def tearDownClass(cls):
        cls.db.execute('delete from "group"')
        cls.db.execute('delete from "user"')

    def test_do_create(self):
        gid = self.model.do_create(self.uid, 'create_test')
        self.assertIsInstance(gid, int)
        self.db.execute('delete from "group" where gid = %s', gid)

    def test_do_join_group(self):
        uid = self.db.getfirstfield("""
            insert into "user"
                   (email, penname, password, is_activated)
            values ('join_test@email.com', 'join_test', 'join_test', true)
            returning uid
        """)
        res = self.model.do_join_group(self.gid, uid)
        assert(res)
        self.db.execute('delete from "user" where uid = %s', uid)

    def test_do_create_topic(self):
        pass

    def test_do_create_chat(self):
        pass

    def test_do_create_bulletin(self):
        pass

    def test_get_group_info(self):
        pass

    def test_get_message(self):
        pass

    def test_get_group_messages(self):
        pass

    def test_get_topic_messages(self):
        pass

    def test_get_chat(self):
        pass

    def test_get_chats(self):
        pass

    def test_get_topic(self):
        pass

    def test_get_topics(self):
        pass

    def test_get_topic_topics(self):
        pass

    def test_get_topic_chats(self):
        pass

    def test_get_member_info(self):
        pass

    def test_get_group_members(self):
        pass

    def test_get_bulletins(self):
        pass

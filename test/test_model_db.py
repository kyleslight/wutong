#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import util
from model.db import Pool


class PoolTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = Pool.instance(util.dsn_test)
        cls.sql = "select %s"
        cls.db.execute("""CREATE TABLE _foo_test (
                              id serial PRIMARY KEY,
                              arg1 int,
                              arg2 varchar(1024)
                          )""")

    @classmethod
    def tearDownClass(cls):
        cls.db.execute("DROP TABLE _foo_test")
        cls.db.release()

    def test_getjson(self):
        sql = 'select row_to_json(j.*) from (select %s as "foo") j'
        res = self.db.getjson(sql, 1)
        self.assertEquals(res, {'foo': 1})

    def test_getfirstfield(self):
        res = self.db.getfirstfield(self.sql, 1)
        self.assertEquals(res, 1)

    def test_row(self):
        res = self.db.getrow(self.sql, 1)
        self.assertEquals(res, (1, ))

    def test_rows(self):
        res = self.db.getrows(self.sql, 1)
        self.assertEquals(res, [(1, )])

    def test_insert(self):
        res = self.db.insert('_foo_test', {'arg1': 1, 'arg2': 'bar'})
        self.assertTrue(res)

    def test_update(self):
        res = self.db.update('_foo_test', {'arg1': 1, 'arg2': 'bar'}, where='1=1')
        self.assertTrue(res)

    def test_delete(self):
        res = self.db.delete('_foo_test', where='1=1')
        self.assertTrue(res)

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

    @classmethod
    def tearDownClass(cls):
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

    def test_execute(self):
        res = self.db.execute(self.sql, 1)
        self.assertTrue(res) 

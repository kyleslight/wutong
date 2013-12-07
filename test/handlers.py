#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import tornado.testing
import requests
from util import path


class TestHandlerBase(unittest.TestCase):

    def setUp(self):
        self.url = "http://localhost:8888"
        self.register_user = {
            "username": "test",
            "password": "test",
            "email": "test@wutong.com",
        }
        self.user = {
            "username": "wutong",
            "password": "wutong",
            "email": "user1@wutong.com",
        }

    def tearDown(self):
        pass


class TestUserHandler(TestHandlerBase):

    def test(self):
        req = requests.post(self.url + "/register", data=self.register_user)
        self.assertEquals(req.text, "success")
        req = requests.post(self.url + "/login", data=self.user)
        self.assertEquals(req.text, "success")
        cookies = req.cookies
        req = requests.get(self.url + "/u/info", cookies=cookies)
        self.assertIsInstance(req.json(), dict)
        req = requests.post(self.url + "/logout", cookies=cookies)
        self.assertEquals(req.text, "success")


class TestGroupHandler(TestHandlerBase):

    def test(self):
        pass

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestUserHandler("test"))
    suite.addTest(TestGroupHandler("test"))
    return suite

def main():
    runner = unittest.TextTestRunner()
    runner.run(suite())

if __name__ == "__main__":
    main()

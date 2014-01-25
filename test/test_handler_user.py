#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: loggerhead
# @Date:   2014-01-22 23:59:37
# @Last Modified by:   fz
# @Last Modified time: 2014-01-25 11:38:16


import unittest
import util
from tornado.web import Application
from tornado.httpclient import HTTPClient
from tornado.httpserver import HTTPRequest
from tornado.testing import AsyncHTTPTestCase
from handler.user import LoginHandler
from handler.user import AvatarHandler


class AvatarHandlerTest(AsyncHTTPTestCase):
    def get_app(self):
        return Application([
            (r'/login', LoginHandler),
            (r'/u/avatar', AvatarHandler),
        ], debug=True)

    def test_set_avatar_from_url(self):
        return
        client = HTTPClient()
        req = HTTPRequest('post', '/login')
        response = client.fetch(req)
        req = HTTPRequest('post', '/u/avatar?v=')
        response = client.fetch(req)
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, 'failed')

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apps import group, account
from tornado.web import RequestHandler
import logging

class RouteHandler(RequestHandler):
	def get(self, filename="group.html"):
		logging.info(filename)
		self.render(filename, messages=[])

urls = [(r"/(.*)", RouteHandler),
        (r"/login", account.LoginHandler),
        (r"/logout", account.LogoutHandler),
        (r"/register", account.RegisterHandler),
        (r"/account/userinfo", account.UserinfoHandler),
        (r"/group/(\w+)/message", group.MessageHandler),
        ]

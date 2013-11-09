#!/usr/bin/env python
# -*- coding: utf-8 -*-

from handler import group, user

urls = [
        (r"/u/home/(\w+)", user.HomeHandler),
        (r"/u/info", user.UserinfoHandler),
        (r"/login", user.LoginHandler),
        (r"/logout", user.LogoutHandler),
        (r"/register", user.RegisterHandler),
        (r"/account/check", user.CheckMailHandler),
        (r"/g/(\w+)", group.IndexHandler),
        (r"/g/(\w+)/message", group.MessageHandler),
    ]

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from handler import group, account

urls = [(r"/", group.IndexHandler),
        (r"/login", account.LoginHandler),
        (r"/logout", account.LogoutHandler),
        (r"/register", account.RegisterHandler),
        (r"/account/userinfo", account.UserinfoHandler),
        (r"/account/check", account.CheckHandler),
        (r"/group/(\w+)", group.IndexHandler),
        (r"/group/(\w+)/message", group.MessageHandler),
        ]

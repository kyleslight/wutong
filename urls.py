#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apps import group, account

urls = [(r"/", group.IndexHandler),
        (r"/group", group.IndexHandler),
        (r"/login", account.LoginHandler),
        (r"/logout", account.LogoutHandler),
        (r"/register", account.RegisterHandler),
        ]

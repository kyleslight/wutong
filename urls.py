#!/usr/bin/env python
# -*- coding: utf-8 -*-

from handler import base, group, user

urls = [
        (r"/u/home/(\w+)", user.HomeHandler),
        (r"/u/info", user.UserinfoHandler),
        (r"/login", user.LoginHandler),
        (r"/logout", user.LogoutHandler),
        (r"/register", user.RegisterHandler),
        (r"/account/check", user.CheckMailHandler),
        (r"/g/(\w+)", group.IndexHandler),
        (r"/g/\w+/groupUserInfo",group.GroupUserInfoHandler),
        (r"/g/(\w+)/groupInfo",group.GroupinfoHandler),
        (r"/g/(\w+)/groupJoinIn",group.JoinHandler),
        (r"/g/(\w+)/message", group.MessageHandler),
        (r"/g/(\w+)/bulletin", group.GroupBulletinHandler),
        (r"/topic/(\w+)", group.TopicHandler),
        # (r"/.*", base.BaseHandler),
    ]

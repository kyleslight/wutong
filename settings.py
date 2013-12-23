#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import uuid
from tornado.options import define, options
from tornado.web import TemplateModule, RequestHandler
from handler import base, group, user, article
import lib.util
from lib.session import Session
from lib.util import encodestr, str2datetime, prettytime


urls = [
    (r"/", group.GroupIndexHandler),
    (r"/u/(\w+)/home", user.HomeHandler),
    (r"/u/info", user.UserinfoHandler),
    (r"/u/permission", user.PermissionHandler),
    (r"/login", user.LoginHandler),
    (r"/logout", user.LogoutHandler),
    (r"/register", user.RegisterHandler),
    (r"/account/check", user.CheckMailHandler),
    (r"/g/browse", group.BrowseHandler),
    (r"/g/create", group.CreateHandler),
    (r"/g/(\d+)", group.GroupIndexHandler),
    (r"/g/(\d+)/info", group.GroupinfoHandler),
    (r"/g/(\d+)/message", group.GroupMessageHandler),
    (r"/g/(\d+)/join", group.JoinHandler),
    (r"/g/(\d+)/permission", group.PermissionHandler),
    (r"/t/(\d+)", group.TopicIndexHandler),
    (r"/t/(\d+)/message", group.TopicMessageHandler),
    (r"/a/browse", article.BrowseArticleHandler),
    (r"/a/create", article.CreateArticleHandler),
    (r"/a/(\d+)", article.OpusHandler),
    (r"/a/(\d+)/comment/bottom", article.BottomCommentHandler),
    (r"/a/(\d+)/comment/side", article.SideCommentHandler),
]


define("host", default="localhost", type=str)
define("port", default=8888, type=int)
define("debug", default=True, type=bool)
define("dbname", default=os.getenv("WUTONG_DB", "wutong"), type=str)
define("dbhost", default=os.getenv("WUTONG_DB_HOST", "localhost"), type=str)
define("dbport", default=os.getenv("WUTONG_DB_PORT", 5432), type=str)
define("dbuser", default=os.getenv("WUTONG_DB_USER", "wutong"), type=str)
define("dbpasswd", default=os.getenv("WUTONG_DB_PASSWD", "wutong"), type=str)
options.parse_command_line()

if options.debug:
    class DebugHandler(RequestHandler):
        def get(self, subpath):
            self.render(subpath)

    urls.append((r"/(.*)", DebugHandler))
    options.dbname += "_test"
else:
    urls.append((r".*", base.BaseHandler))

class MyModule(TemplateModule):
    def render(self, path, **kwargs):
        path = os.path.join("modules", path)
        return super(MyModule, self).render(path, **kwargs)


settings = dict(
    sitename=u"梧桐".encode("utf8"),
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    xsrf_cookies=False,
    login_url="/login",
    host=options.host,
    port=options.port,
    debug=options.debug,
    cookie_secret=str(options.debug or uuid.uuid1().hex),
    session_secret=str(options.debug or uuid.uuid4().hex),
    encrypt_url="encrypt.wutong.com",
    ui_modules={
        "MyModule": MyModule,
    },
    ui_methods = {
        "encodestr": lambda h, x: encodestr(x),
        "str2datetime": lambda h, x: str2datetime(x),
        "prettytime": lambda h, x: prettytime(x),
    },
    dsn="dbname=" + options.dbname      \
       +" user=" + options.dbuser       \
       +" password=" + options.dbpasswd \
       +" host=" + options.dbhost       \
       +" port=" + str(options.dbport)
)


Session.register(settings["session_secret"])
lib.util.encrypt_url = settings.get("encrypt_url")

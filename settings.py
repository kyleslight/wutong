#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path, getenv
from uuid import uuid5, NAMESPACE_OID
from tornado.options import define, options
from lib.session import Session
from handler import base, group, user


define("host", default="localhost", type=str)
define("port", default=8888, type=int)
define("debug", default=True, type=bool)
define("dbname", default=getenv("WUTONG_DB", "wutong"), type=str)
define("dbhost", default=getenv("WUTONG_DB_HOST", "localhost"), type=str)
define("dbport", default=getenv("WUTONG_DB_PORT", 5432), type=str)
define("dbuser", default=getenv("WUTONG_DB_USER", "wutong"), type=str)
define("dbpasswd", default=getenv("WUTONG_DB_PASSWD", "wutong"), type=str)
options.parse_command_line()

settings = dict(
    sitename=u"梧桐".encode("utf8"),
    template_path=path.join(path.dirname(__file__), "templates"),
    static_path=path.join(path.dirname(__file__), "static"),
    xsrf_cookies=False,
    login_url="/login",
    host=options.host,
    port=options.port,
    debug=options.debug,
)

settings["cookie_secret"] = str(uuid5(NAMESPACE_OID, settings["sitename"]))
settings["session_secret"] = str(uuid5(NAMESPACE_OID, settings["cookie_secret"]))
Session.register(settings["session_secret"])

urls = [
    (r"/", user.HomeHandler),
    (r"/u/home/(\w+)", user.HomeHandler),
    (r"/u/info", user.UserinfoHandler),
    (r"/login", user.LoginHandler),
    (r"/logout", user.LogoutHandler),
    (r"/register", user.RegisterHandler),
    (r"/account/check", user.CheckMailHandler),
    (r"/g/(\w+)", group.IndexHandler),
    (r"/g/\w+/groupJoin",group.JoinHandler),
    (r"/g/(\w+)/message", group.MessageHandler),
    (r"/t/(\w+)", group.TopicHandler),
]


if settings["debug"]:
    options.dbname += "_test"

    from tornado.web import RequestHandler
    class DebugHandler(RequestHandler):
        def get(self, subpath):
            self.render(subpath)

    urls.append((r"/(.*)", DebugHandler))


settings["dsn"] = "dbname=" + options.dbname      \
                + " user=" + options.dbuser       \
                + " password=" + options.dbpasswd \
                + " host=" + options.dbhost       \
                + " port=" + str(options.dbport)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os import path, environ
from uuid import uuid5, NAMESPACE_OID
from tornado.options import define, options
from lib.session import Session

define("host", default="localhost", type=str)
define("port", default=8888, type=int)
define("debug", default=True, type=bool)
define("dbname", default=environ.get("WUTONG_DB", "wutong"), type=str)
define("dbhost", default=environ.get("WUTONG_HOST", "localhost"), type=str)
define("dbport", default=environ.get("WUTONG_PORT", 5432), type=str)
define("dbuser", default=environ.get("WUTONG_USER", "wutong"), type=str)
define("dbpasswd", default=environ.get("WUTONG_PASSWD", "wutong"), type=str)
options.parse_command_line()

settings = dict(
        sitename=u"梧桐".encode("utf8"),
        template_path=path.join(path.dirname(__file__), "templates"),
        static_path=path.join(path.dirname(__file__), "static"),
        xsrf_cookies=False,
        login_url="/login",
        autoescape=None,
        host=options.host,
        port=options.port,
        debug=options.debug,
    )

settings["cookie_secret"] = str(uuid5(NAMESPACE_OID, settings["sitename"]))
settings["session_secret"] = str(uuid5(NAMESPACE_OID, settings["sitename"]))

if settings["debug"]:
    options.dbname += "_test"
settings["dsn"] = "dbname=%s user=%s password=%s host=%s port=%s" % (
                       options.dbname, options.dbuser, options.dbpasswd,
                       options.dbhost, options.dbport
                    )

Session.register(settings["session_secret"])

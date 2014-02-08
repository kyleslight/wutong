#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import uuid
from tornado.options import define, options
from tornado.web import UIModule, TemplateModule, RequestHandler
from handler import base, group, user, article, upload, search
import lib.util
from lib.session import Session
from lib import util


urls = [
    (r"/", user.IndexHandler),
    (r"/login", user.LoginHandler),
    (r"/logout", user.LogoutHandler),
    (r"/register", user.RegisterHandler),
    (r"/account", user.AccountHandler),
    (r"/upload", upload.FileHandler),
    (r"/search", search.SearchHandler),
    (r"/tag/(.+)", base.BaseHandler),
    (r"/user/(.+)", user.HomeHandler),
    (r"/u/info", user.UserinfoHandler),
    (r"/u/memo", user.MemoHandler),
    (r"/u/collection", user.CollectionHandler),
    (r"/a/browse", article.BrowseHandler),
    (r"/a/create", article.CreateHandler),
    (r"/a/(\d+)", article.OpusHandler),
    (r"/a/(\d+)/score", article.ArticleScoreHandler),
    (r"/a/(\d+)/collection", article.ArticleCollectionHandler),
    (r"/a/(\d+)/comment/bottom", article.BottomCommentHandler),
    (r"/a/(\d+)/comment/side", article.SideCommentHandler),
    (r"/g/browse", group.BrowseHandler),
    (r"/g/create", group.CreateHandler),
    (r"/g/(\d+)", group.GroupIndexHandler),
    (r"/g/(\d+)/info", group.GroupinfoHandler),
    (r"/g/(\d+)/message/websocket", group.GroupMessageSocketHandler),
    (r"/g/(\d+)/message", group.GroupMessageHandler),
    (r"/g/(\d+)/join", group.JoinHandler),
    (r"/g/(\d+)/permission", group.PermissionHandler),
    (r"/t/(\d+)", group.TopicIndexHandler),
    (r"/t/(\d+)/message/websocket", group.TopicMessageSocketHandler),
    (r"/t/(\d+)/message", group.TopicMessageHandler),
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
    class DebugHandler(base.BaseHandler):
        def get(self, subpath):
            valids = ['html', 'htm', 'xml']
            suffix = subpath.rsplit('.', 1)[-1]

            if suffix in valids:
                self.render(subpath)
            else:
                self.render_404_page()

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
        "encodestr": lambda handler, x: util.encodestr(x),
        "str2datetime": lambda handler, x: util.str2datetime(x),
        "prettytime": lambda handler, x: util.prettytime(x),
        "avatarurl": lambda handler, x, *arg: util.avatarurl(x, *arg),
        "getuser": lambda handler: handler.get_current_user(),
    },
    dsn="dbname=%s user=%s password=%s host=%s port=%s" % (
        options.dbname,
        options.dbuser,
        options.dbpasswd,
        options.dbhost,
        str(options.dbport),
    )
)
settings['avatar_path'] = os.path.join(settings['static_path'], "avatar")


Session.register(settings["session_secret"])
lib.util.encrypt_url = settings.get("encrypt_url")

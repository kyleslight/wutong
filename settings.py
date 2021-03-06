#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import uuid
from tornado.options import define, options
from tornado.web import UIModule, TemplateModule, RequestHandler
from handler import base, group, user, article, userfile, search
import lib.util
from lib.session import Session
from lib import util


urls = [
    (r"/", user.IndexHandler),
    (r"/login", user.LoginHandler),
    (r"/logout", user.LogoutHandler),
    (r"/register", user.RegisterHandler),
    (r"/account", user.AccountHandler),
    (r"/file/upload", userfile.UploadHandler),
    (r"/file/download", userfile.DownloadHandler),
    (r"/picture", userfile.PictureHandler),
    (r"/search", search.SearchHandler),
    (r"/user/(.+)", user.HomeHandler),
    (r"/u/avatar", userfile.UserAvatarHandler),
    (r"/u/info", user.UserinfoHandler),
    (r"/u/memo", user.MemoHandler),
    (r"/u/message", user.MessageHandler),
    (r"/u/collection", user.CollectionHandler),
    (r"/u/star", user.StarHandler),
    (r"/a/browse", article.BrowseHandler),
    (r"/a/create", article.CreateHandler),
    (r"/a/(\d+)", article.ArticleHandler),
    (r"/a/(\d+)/update", article.UpdateHandler),
    (r"/a/(\d+)/comment", article.CommentHandler),
    (r"/a/(\d+)/interact", article.InteractHandler),
    (r"/g/create", group.CreateHandler),
    (r"/g/browse", group.BrowseHandler),
    (r"/g/browse/topic", group.BrowseMoreTopicHandler),
    (r"/g/(\d+)/join", group.JoinHandler),
    (r"/g/(\d+)/member", group.GroupMemberHandler),
    (r"/g/(\d+)/article", group.GroupArticleHandler),
    (r"/g/(\d+)", group.GroupHandler),
    (r"/g/(\d+)/session/history", group.GroupSessionHistoryHandler),
    (r"/g/(\d+)/session/websocket", group.GroupSessionWebsocketHandler),
    (r"/g/(\d+)/session/ajax", group.GroupSessionAjaxHandler),
    (r"/t/(\d+)", group.TopicHandler),
    (r"/t/(\d+)/session/history", group.TopicSessionHistoryHandler),
    (r"/t/(\d+)/session/websocket", group.TopicSessionWebsocketHandler),
    (r"/t/(\d+)/session/ajax", group.TopicSessionAjaxHandler),
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
                # self.render_404_page()
                pass

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
    },
    dsn="dbname=%s user=%s password=%s host=%s port=%s" % (
        options.dbname,
        options.dbuser,
        options.dbpasswd,
        options.dbhost,
        str(options.dbport),
    )
)
settings['upload_path'] = os.path.join(settings['static_path'], "uploads")
settings['avatar_path'] = os.path.join(settings['static_path'], "avatar")


Session.register(settings["session_secret"])
lib.util.encrypt_url = settings.get("encrypt_url")

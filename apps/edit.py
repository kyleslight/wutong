#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import asynchronous, RequestHandler
from tornado import template
from tornado import gen
import momoko
import tornado
import tornado.escape

class BaseHandler(RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        user_id = self.get_secure_cookie("user_id")
        if not user_id: return None
        return tornado.escape.json_decode(user_id)

class IndexHandler(BaseHandler):
    def get(self):
        return self.render("index.html")

    @asynchronous
    @gen.engine
    def post(self):
        msgs = []
        title = self.get_argument("title", None)
        describe = self.get_argument("describe", None)
        context = self.get_argument("context", None)

        if title is None: msgs.append(u'请输入标题')
        if describe is None: msgs.append(u'描述不能为空')
        if context is None: msgs.append(u'正文不能为空')

        if not msgs:
            cursor = yield momoko.Op(self.db.execute,
                                     'INSERT INTO article (title, describe, contenxt) VALUES (%s, %s, %s) RETURNING id;',
                                     (title, describe, context)
            )
            result = cursor.fetchone()
            id = result[0]
            self.redirect("show", str(id))
            return

        self.render("index.html", msgs=msgs)

class ShowHandler(BaseHandler):
    def get(self, id):
        return self.render("show.html")
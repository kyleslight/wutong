#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Last Modified: 2013-11-10 14:29:17

import logging
from datetime import datetime
from tornado.web import authenticated
from tornado.websocket import WebSocketHandler
from tornado.escape import json_encode, json_decode
from base import BaseHandler

class GroupBaseHandler(BaseHandler):

    @property
    def model(self):
        return self.groupmodel

    def render_message(self, message):
        rmsg = self.render_string("message.html", message=message)
        rmsg = to_basestring(rmsg)
        return rmsg

    def get_messages(self, gid, size=30, offset=0):
        messages = self.model.get_group_messages(gid, size, offset)
        if not messages:
            messages = []
        return messages

class IndexHandler(GroupBaseHandler):

    def render_messages(self, messages):
        rmsgs = []
        for message in messages:
            rmsgs.append(self.render_message(message))
        return rmsgs

    def get(self, gid):
        messages = self.get_messages(gid)
        logging.info('-' * 80)
        logging.info(messages)
        messages = self.render_messages(messages)
        self.render("group.html", messages=messages)

class MessageHandler(GroupBaseHandler, WebSocketHandler):
    members = dict()

    def is_member(self, uid):
        return True

    def open(self, gid):
        self.gid = gid
        if not self.members.get(gid, None):
            self.members[gid] = list()

        self.members[gid].append(self)
        self.user = self.get_current_user()

    def on_close(self):
        self.members[self.gid].remove(self)

    def on_message(self, json_data):
        uid=self.user["uid"]
        if json_data and self.is_member(uid):
            data = json_decode(json_data)
            content = data["content"]
            title = data["title"]

            if title:
                self.db.insert_group_topic(self.gid, uid, content, title)
            else:
                self.db.insert_group_chat(self.gid, uid, content)

            entry = dict(
                    penname=self.user["penname"],
                    content=content,
                    submit_time=str(datetime.now()),
                    avatar=self.user["avatar"],
                    title=title,
                )
            logging.info(entry)
            for self.mem in self.members[self.gid]:
                self.mem.write_message(json_encode(entry))



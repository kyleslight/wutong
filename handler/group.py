#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Last Modified: 2013-11-10 14:29:17

import logging
from datetime import datetime
from tornado.web import authenticated
from tornado.websocket import WebSocketHandler
from tornado.escape import json_encode, json_decode, to_basestring
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

    def get(self, gid):
        self.render("group.html")


class MessageHandler(GroupBaseHandler, WebSocketHandler):
    members = dict()

    def add_session(self):
        if not MessageHandler.members.get(self.gid, None):
            MessageHandler.members[self.gid] = list()
        MessageHandler.members[self.gid].append(self)

    def get_member_info(self, uid):
        return self.model.get_member_info(self.gid, uid)

    def send_message(self, message):
        message["user"] = self.usermodel.get_user_info_by_uid(message["uid"])
        self.write_message(json_encode(message))

    def send_message_to_all(self, message_id):
        message = self.model.get_group_message(message_id)
        for member in MessageHandler.members[self.gid]:
            member.send_message(message)

    def save_message(self, message):
        return self.model.do_insert_message(
                self.gid,
                message["uid"],
                message["content"],
                message.get("title", None),
                message.get("reply_id", None),
            )

    def open(self, gid):
        self.gid = gid
        self.add_session()
        messages = self.get_messages(gid)
        while messages:
            self.send_message(messages.pop())

    def on_close(self):
        MessageHandler.members[self.gid].remove(self)

    def on_message(self, message):
        uid = self.is_authenticated()
        if not self.get_member_info(uid):
            return
        message = json_decode(message)
        message["uid"] = uid
        message_id = self.save_message(message)
        self.send_message_to_all(message_id)


class TopicHandler(GroupBaseHandler):

    def get(self, topic_id):
        self.render("groupTest.html")


class JoinHandler(GroupBaseHandler):

    def post(self):
        uid = self.get_argument("uid", None)
        gid = self.get_argument("gid", None)
        self.model.do_user_join_group(gid, uid)

class GroupinfoHandler(GroupBaseHandler):

    def get(self, gid):
        group_info = self.model.get_group_info(gid)
        group_info = json_encode(group_info)
        self.write(group_info)

    @authenticated
    def post(self, gid):
        name = self.get_argument("groupname", None)
        intro = self.get_argument("groupintro", None)
        motton = self.get_argument("groupmotton", None)
        user = self.get_current_user()
        founder = user["penname"]
        self.model.update_group_info(gid, founder, name, intro, motton)

class GroupUserInfoHandler(GroupBaseHandler):

    def post(self):
        uid = self.get_argument("uid", None)
        gid = self.get_argument("gid", None)
        member_info = self.model.get_member_info(gid, uid)
        member_info = json_encode(member_info)
        self.write(member_info)

class GroupBulletinHandler(GroupBaseHandler):

    def get(self, gid):
        bulletins = self.model.get_group_bulletins(gid, 6, 0)
        while bulletins:
            self.write(bulletins.pop())

    def post(self, gid):
        content = self.get_argument("content", None)
        title = self.get_argument("title", None)
        self.do_insert_bulletin(gid, self.user_id, content, title)

class GroupMembersHandler(GroupBaseHandler):

    def get(self, gid):
        pass

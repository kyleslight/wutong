#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.websocket import WebSocketHandler
from tornado.escape import json_decode, json_encode
from base import BaseHandler


class GroupBaseHandler(BaseHandler):
    @property
    def model(self):
        return self.groupmodel

    def get_group_info(self, gid):
        group_info = self.model.get_group_info(gid)
        return group_info

    def get_bulletins(self, gid):
        bulletins = self.model.get_bulletins(gid, 6, 0)
        return bulletins or []

    def get_member_info(self, gid, uid):
        member_info = self.model.get_member_info(gid, uid)
        return member_info

    def get_group_members(self, gid):
        members = self.model.get_group_members(gid, 30, 0)
        return members

    def is_group_public(self, gid):
        group_info = self.get_group_info(gid)
        return group_info["is_public"]

    def is_group_member(self, gid):
        if not hasattr(self, "_member_info"):
            self._member_info = self.get_member_info(gid, self.user_id)
        return self._member_info.get("is_member", False)

    def is_group_subleader(self, gid):
        if not hasattr(self, "_member_info"):
            self._member_info = self.get_member_info(gid, self.user_id)
        return self._member_info.get("is_subleader", False)

    def is_group_leader(self, gid):
        if not hasattr(self, "_member_info"):
            self._member_info = self.get_member_info(gid, self.user_id)
        return self._member_info.get("is_leader", False)


class MessageBaseHandler(GroupBaseHandler):
    @property
    def gid(self):
        if not hasattr(self, "_gid"):
            self._gid = None
        return self._gid

    @gid.setter
    def gid(self, value):
        self._gid = value

    @property
    def reply_id(self):
        if not hasattr(self, "_tid"):
            return None
        return self._tid

    @reply_id.setter
    def reply_id(self, value):
        self._tid = value

    def get_topic(self, tid):
        topic = self.model.get_topic(tid)
        return topic

    def get_topic_group(self, tid):
        topic = self.get_topic(tid)
        group_info = self.model.get_group_info(topic["gid"])
        return group_info

    def get_topic_messages(self, tid):
        messages = self.model.get_topic_messages(tid, 30, 0)
        return messages or []

    def get_group_messages(self, gid):
        messages = self.model.get_group_messages(gid, 30, 0)
        return messages or []

    def get_message(self, message_id):
        message = self.model.get_message(message_id)
        return message

    def save_message(self, message):
        if message.has_key("title"):
            id = self.model.do_create_topic(
                self.gid,
                self.user_id,
                message["title"],
                message["content"],
                self.reply_id
            )
        else:
            id = self.model.do_create_chat(
                self.gid,
                self.user_id,
                message["content"],
                self.reply_id
            )
        return id

    def save_and_render_message(self, message):
        id = self.save_message(message)
        msg = self.get_message(id)
        return self.render_module_string("message.html", message=msg)


class PermissionHandler(GroupBaseHandler):
    def post(self, gid):
        check = self.get_argument("check_permission")
        if check == "is_public":
            if self.is_group_public(gid):
                self.write("true")
            else:
                self.write("false")
        elif check == "is_member":
            if self.is_group_member(gid):
                self.write("true")
            else:
                self.write("false")
        elif check == "is_leader":
            if self.is_group_leader(gid):
                self.write("true")
            else:
                self.write("false")
        elif check == "is_subleader":
            if self.is_group_subleader(gid):
                self.write("true")
            else:
                self.write("false")


class JoinHandler(GroupBaseHandler):
    def join_group(self, gid, uid):
        return self.model.do_join_group(gid, uid)

    def post(self, gid):
        if self.join_group(gid, self.user_id):
            self.write("success")
        else:
            self.write("failed")


class GroupinfoHandler(GroupBaseHandler):
    def is_visible(self, gid):
        return self.is_group_public(gid) or self.is_group_member(gid)

    def get(self, gid):
        if not self.is_visible(gid):
            self.write("not group member")
            return
        group_info = self.get_group_info(gid)
        group_info = json_encode(group_info)
        self.write(group_info)


class GroupIndexHandler(MessageBaseHandler):
    def get(self, gid):
        group_info = self.get_group_info(gid)
        if not group_info:
            self.write_error(403)
            return

        bulletins = self.get_bulletins(gid)
        messages = self.get_group_messages(gid)
        members = self.get_group_members(gid)
        self.render(
                "group.html",
                bulletins=bulletins,
                messages=messages,
                members=members,
                group_info=group_info
            )


class TopicIndexHandler(MessageBaseHandler):
    def get_ancestor_topics(self):
        tpc = self.topic
        topics = [tpc]
        while tpc["reply_id"]:
            father_tid = tpc["reply_id"]
            tpc = self.get_topic(father_tid)
            topics.append(tpc)
        return topics

    def get(self, tid):
        self.topic = self.get_topic(tid)
        if not self.topic:
            self.write_error(403)
            return
        else:
            self.gid = self.topic["gid"]

        ancestor_topics = self.get_ancestor_topics()
        group_info = self.get_group_info(self.gid)
        bulletins = self.get_bulletins(self.gid)
        messages = self.get_topic_messages(tid)
        self.render(
                "topic.html",
                ancestor_topics=ancestor_topics.__reversed__(),
                topic=self.topic,
                bulletins=bulletins,
                messages=messages,
                group_info=group_info
            )


class MessageSocketHandler(MessageBaseHandler, WebSocketHandler):
    @property
    def manager(self):
        cls = type(self)
        if not hasattr(cls, "_manager"):
            cls._manager = dict()
        return cls._manager

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    def add(self):
        if not self.manager.has_key(self.id):
            self.manager[self.id] = set()
        self.manager[self.id].add(self)

    def remove(self):
        handlers = self.manager.get(self.id)
        if handlers:
            handlers.discard(self)

    def send_message(self, message):
        for handler in self.manager[self.id]:
            handler.write_message(message)

    @property
    def user_id(self):
        return self.session.load().get("uid")

    def can_send_message(self):
        member_info = self.model.get_member_info(self.gid, self.user_id)
        if member_info:
            return True
        else:
            return False

    def on_message(self, message):
        if self.can_send_message():
            msg = json_decode(message)
            msg = self.save_and_render_message(msg)
            if msg:
                self.send_message(msg)
            else:
                pass
                # self.write_message("failed")

    def on_close(self):
        self.remove()


class GroupMessageHandler(MessageSocketHandler):
    def open(self, gid):
        self.gid = self.id = gid
        self.add()


class TopicMessageHandler(MessageSocketHandler):
    def get_topic(self, tid):
        return self.model.get_topic(tid)

    def open(self, tid):
        self.id = tid
        self.reply_id = tid
        self.gid = self.get_topic(tid)["gid"]
        self.add()

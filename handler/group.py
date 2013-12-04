#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Last Modified: 2013-11-10 14:29:17

from tornado.web import authenticated, asynchronous
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
        messages = self.model.get_chats(gid, size, offset)
        if not messages:
            messages = []
        return messages


class IndexHandler(GroupBaseHandler):

    def get_render_communications(self, gid):
        topics = self.model.get_topics(gid, 30, 0)
        chats = self.model.get_chats(gid, 30, 0)
        comms = []
        if topics:
            comms += topics
        if chats:
            comms += chats

        def cmp(comm1, comm2):
            topic_or_chat1 = comm1.has_key("tid")
            topic_or_chat2 = comm2.has_key("tid")

            if topic_or_chat1 != topic_or_chat2:
                return comm1["submit_time"] < comm2["submit_time"]
            if topic_or_chat1:
                return comm1["tid"] < comm2["tid"]
            else:
                return comm1["id"] < comm2["id"]

        sorted(comms, cmp=cmp, reverse=True)
        redrs = []
        for comm in comms:
            if comm.has_key("tid"):
                redr = self.render_string("modules/topic.html", topic=comm)
            else:
                redr = self.render_string("modules/chat.html", chat=comm)
            redrs.append(redr)

        return redrs

    def get_render_group_info(self, gid):
        group_info = self.model.get_group_info(gid)
        return self.render_string("modules/group_info.html", group_info=group_info)

    def get_render_bulletins(self, gid):
        bulletins = self.model.get_bulletins(gid, 6, 0)
        print(bulletins[0])

        redrs = []
        for blt in bulletins:
            redr = self.render_string("modules/bulletin.html", bulletin=blt)
            redrs.append(redr)

        return redrs

    def get(self, gid):
        try:
            gid = int(gid)
        except ValueError:
            self.write_error(403)
            return
        comms = self.get_render_communications(gid)
        group_info = self.get_render_group_info(gid)
        bulletins = self.get_render_bulletins(gid)
        self.render("group.html", bulletins=bulletins, communications=comms, group_info=group_info)


class MessageHandler(GroupBaseHandler, WebSocketHandler):
    members = dict()

    def add_session(self):
        if not MessageHandler.members.get(self.gid, None):
            MessageHandler.members[self.gid] = list()
        MessageHandler.members[self.gid].append(self)

    def get_member_info(self, uid):
        return self.model.get_member_info(self.gid, uid)

    def send_message(self, message):
        message["user"] = self.usermodel.get_user_info(message["uid"])
        self.write_message(json_encode(message))

    def save_and_send_message(self, message):
        if message.has_key("title"):
            tid = self.model.do_create_topic(
                    self.gid,
                    message["uid"],
                    message["title"],
                    message["content"],
                    message.get("reply_id", None)
                )
            message = self.model.get_topic(tid)
        else:
            id = self.model.do_create_chat(
                    self.gid,
                    message["uid"],
                    message["content"],
                    message.get("reply_id", None)
                )
            message = self.model.get_chat(id)

        for member in MessageHandler.members[self.gid]:
            member.send_message(message)

    def open(self, gid):
        self.gid = gid
        self.add_session()

    def on_close(self):
        MessageHandler.members[self.gid].remove(self)

    def on_message(self, message):
        uid = self.is_authenticated()
        if not self.get_member_info(uid):
            return
        message = json_decode(message)
        message["uid"] = uid
        self.save_and_send_message(message)


class TopicHandler(GroupBaseHandler):

    def get_render_communications(self, tid):
        topics = self.model.get_topic_topics(tid, 30, 0)
        chats = self.model.get_topic_chats(tid, 30, 0)
        comms = []
        if topics:
            comms += topics
        if chats:
            comms += chats

        def cmp(comm1, comm2):
            topic_or_chat1 = comm1.has_key("tid")
            topic_or_chat2 = comm2.has_key("tid")

            if topic_or_chat1 != topic_or_chat2:
                return comm1["submit_time"] < comm2["submit_time"]
            if topic_or_chat1:
                return comm1["tid"] < comm2["tid"]
            else:
                return comm1["id"] < comm2["id"]

        sorted(comms, cmp=cmp, reverse=True)
        redrs = []
        for comm in comms:
            if comm.has_key("tid"):
                redr = self.render_string("modules/topic.html", topic=comm)
            else:
                redr = self.render_string("modules/chat.html", chat=comm)
            redrs.append(redr)

        return redrs

    def get_topic_paths(self, topic):
        topics = [topic]
        while topic["reply_id"]:
            topic = self.model.get_topic(topic["reply_id"])
            topics.append(topic)
        return topics.__reversed__()

    def get(self, topic_id):
        comms = self.get_render_communications(topic_id)
        topic = self.model.get_topic(topic_id)
        topics = self.get_topic_paths(topic)
        self.render("groupTest.html", topic_paths=topics, topic=topic, communications=comms)


class JoinHandler(GroupBaseHandler):

    def post(self):
        uid = self.get_argument("uid", None)
        gid = self.get_argument("gid", None)
        self.model.do_user_join_group(gid, uid)
        self.write("success")


class GroupinfoHandler(GroupBaseHandler):

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

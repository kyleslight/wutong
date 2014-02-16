#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import asynchronous, authenticated
from tornado.websocket import WebSocketHandler
from tornado.escape import json_decode, json_encode
from base import BaseHandler
from lib import util


class BrowseHandler(BaseHandler):
    def get(self):
        try:
            user = self.current_user
            if user:
                user['groups'] = self.mgroup.get_user_groups(user['uid'], 1, 20)
                user['topics'] = self.mgroup.get_mygroup_topics(user['uid'], 1, 10)
                size = 10
            else:
                size = 20
            topics = self.mgroup.get_topics(1, size)

            self.render(
                'group-navigation.html',
                user=user,
                topics=topics
            )
        except Exception as e:
            self.write_errmsg(e)


class BrowseTopicHandler(BaseHandler):
    def get(self):
        try:
            topic_type = self.get_argument('type')
            page = int(self.get_argument('page'))
            size = int(self.get_argument('size', 10))
            if topic_type == 'mygroup':
                topics = self.mgroup.get_mygroup_topics(self.user_id, page, size)
            elif topic_type == 'all':
                topics = self.mgroup.get_topics(page, size)
            else:
                raise Exception('invalid type')
            self.write_json(topics)
        except Exception as e:
            self.write_errmsg(e)


class CreateHandler(BaseHandler):
    def get_tags(self):
        tags = self.args.get('tags')
        tags = util.split(tags)
        return tags

    @authenticated
    def post(self):
        try:
            self.get_args('name', 'intro', 'public_level', 'tags')
            self.set_arg('tags', self.get_tags())
            group_id = self.mgroup.do_create(self.user_id, **self.args)
            self.redirect('/g/' + str(group_id))
        except Exception as e:
            self.write_errmsg(e)


class JoinHandler(BaseHandler):
    @authenticated
    def post(self, group_id):
        try:
            self.join_group(group_id, self.user_id)
        except Exception as e:
            self.write_errmsg(e)


class GroupHandler(BaseHandler):
    def get(self, group_id):
        group = self.mgroup.get_group_homepage(group_id)
        if group:
            self.render('group.html', group=group)
        else:
            self.render_404_page()


class GroupSessionHistoryHandler(BaseHandler):
    def get(self, group_id):
        if not self.mgroup.is_group_visiable(group_id, self.user_id):
            self.write_errmsg('no access permission')
            return
        page = int(self.get_argument('page'))
        size = int(self.get_argument('20'))
        ss = self.mgroup.get_group_sessions(group_id, page, size)
        self.write_json(ss)


# TODO
class TopicHandler(BaseHandler):
    def get(self, topic_id):
        pass


# TODO
class MessageBaseHandler(BaseHandler):
    _group_manager = dict()
    _topic_manager = dict()

    @property
    def user_id(self):
        return self.session.load().get("uid")

    def init_content(self, id, **kwargs):
        """Call this function immediately after connected with client"""
        self.id = id
        name = self.__class__.__name__.lower()
        if 'group' in name:
            self.manager = self._group_manager
            self.gid = self.id
            self.reply_id = None
        elif 'topic' in name:
            self.manager = self._topic_manager
            self.tid = self.id
            self.reply_id = self.tid
            self.gid = self.get_topic(self.tid)["gid"]

    def add(self, handler):
        if not self.manager.has_key(self.id):
            self.manager[self.id] = set()
        self.manager[self.id].add(handler)

    def remove(self, handler):
        self.manager.get(self.id).discard(handler)

    def send_message(self, message):
        trash = set()
        for handler in self.manager[self.id]:
            handler = handler.write_message(message)
            trash.add(handler)
        self.manager[self.id] -= trash

    def can_send_message(self):
        member_info = self.mgroup.get_member_info(self.gid, self.user_id)
        if member_info:
            return True
        else:
            return False

    def on_message(self, message):
        if not self.can_send_message():
            self.error('not login')
            return
        msg = json_decode(message)
        mid = self.save_message(msg)
        msg = self.get_message(mid)
        msg = self.render_module_string("message.html", message=msg)
        self.send_message(msg)

    def save_message(self, message):
        if message.has_key("title"):
            id = self.mgroup.do_create_topic(
                self.gid,
                self.user_id,
                message["title"],
                message["content"],
                self.reply_id
            )
        else:
            id = self.mgroup.do_create_chat(
                self.gid,
                self.user_id,
                message["content"],
                self.reply_id
            )
        return id

    def get_topic(self, tid):
        topic = self.mgroup.get_topic(tid)
        return topic

    def get_topic_group(self, tid):
        topic = self.get_topic(tid)
        group_info = self.mgroup.get_group_info(topic["gid"])
        return group_info

    def get_topic_sessions(self, tid):
        messages = self.mgroup.get_topic_sessions(tid, 30, 0)
        return messages or []

    def get_group_sessions(self, gid):
        messages = self.mgroup.get_group_sessions(gid, 30, 0)
        return messages or []

    def get_message(self, message_id):
        message = self.mgroup.get_message(message_id)
        return message


class MessageHandler(MessageBaseHandler):
    @asynchronous
    def get(self, id):
        self.init_content(id)
        self.add(self)

    def post(self, id):
        self.init_content(id)
        data = self.request.body
        self.on_message(data)

    # return handler which should be delete
    def write_message(self, message):
        if self.request.connection.stream.closed():
            return
        self.write(message)
        self.finish()
        return self


class GroupMessageHandler(MessageHandler):
    pass


class TopicMessageHandler(MessageHandler):
    pass


class MessageSocketHandler(MessageBaseHandler, WebSocketHandler):
    def error(self, message):
        self.write_message(message)

    def open(self, id):
        self.init_content(id)
        self.add(self)

    def on_close(self):
        self.remove(self)


class GroupMessageSocketHandler(MessageSocketHandler):
    pass


class TopicMessageSocketHandler(MessageSocketHandler):
    pass

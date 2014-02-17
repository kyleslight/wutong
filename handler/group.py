#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import asynchronous, authenticated
from tornado.websocket import WebSocketHandler
from tornado.escape import json_decode, json_encode
from base import BaseHandler, SessionBaseHandler
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
        anchor_id = int(self.get_argument('anchor_id'))
        size = int(self.get_argument('size', 20))
        ss = self.mgroup.get_group_sessions(group_id, anchor_id, size)
        self.write_json(ss)


# TODO
class TopicHandler(BaseHandler):
    def get(self, topic_id):
        pass


class GroupSessionBaseHandler(SessionBaseHandler):
    def get_reply_topic_id(self):
        """
        """
        return None

    def format_message(self, message):
        if not self.mgroup.is_group_member(self.group_id, self.user_id):
            raise Exception('not group member')
        message = json_decode(message)
        if message['type'] == 'message':
            if not message.has_key('content'):
                raise Exception('no content')
        elif message['type'] == 'topic':
            if not message.has_key('title'):
                raise Exception('no title')
            if not message.has_key('content'):
                raise Exception('no content')
        else:
            raise Exception('invalid message type')
        return message

    def save_message(self, message):
        if message['type'] == 'message':
            message = self.mgroup.create_group_message(
                self.group_id,
                self.user_id,
                message['content'],
                self.get_reply_topic_id()
            )
        elif message['type'] == 'topic':
            message = self.mgroup.create_group_topic(
                self.group_id,
                self.user_id,
                message['title'],
                message['content'],
                self.get_reply_topic_id()
            )
        return message


class GroupSessionAjaxHandler(SessionBaseHandler):
    def get_father_topic_id(self):
        return None

    def format_message(self, message):
        format_message(self, message)

    def save_message(self, message):
        save_message(self, message)

    def get(self, group_id):
        self.channel = 'g' + str(group_id)
        self.group_id = group_id
        self.listen()

    def post(self, group_id):
        self.channel = 'g' + str(group_id)
        self.group_id = group_id
        message = self.get_argument('message')
        self.send_message(message)


class TopicSessionAjaxHandler(SessionBaseHandler):
    pass


class GroupSessionWebsocketHandler(GroupSessionBaseHandler, WebSocketHandler):
    def open(self, group_id):
        self.channel = 'g' + str(group_id)
        self.group_id = group_id
        if not self.mgroup.is_group_visiable(self.group_id, self.user_id):
            self.write_errmsg('no access permission')
            return
        self.listen()

    def on_message(self, message):
        self.send_message(message)


# TODO
class TopicSessionWebsocketHandler(GroupSessionBaseHandler, WebSocketHandler):
    def get_reply_topic_id(self):
        return self.topic['id']

    def open(self, topic_id):
        self.channel = 't' + str(topic_id)
        self.topic = self.mgroup.get_topic(topic_id)
        self.group_id = self.topic['gid']
        if not self.mgroup.is_group_visiable(self.group_id, self.user_id):
            self.write_errmsg('no access permission')
            return
        self.listen()

    def on_message(self, message):
        self.send_message(message)

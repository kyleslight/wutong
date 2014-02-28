#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import asynchronous
from tornado.websocket import WebSocketHandler
from tornado.escape import json_decode, json_encode
from base import BaseHandler, SessionBaseHandler, authenticated, catch_exception
from lib import util


class BrowseHandler(BaseHandler):
    @catch_exception
    def get(self):
        tag = self.get_argument('tag')
        if tag:
            # groups = self.mgroup.get_public_groups()
            self.write_json(groups)
            return

        user = self.current_user
        if user:
            user['groups'] = self.mgroup.get_user_groups(user['uid'], 1, 20)
            user['topics'] = self.mgroup.get_mygroup_topics(user['uid'], 1, 10)
            size = 10
        else:
            size = 20
        topics = self.mgroup.get_browse_topics(1, size)

        self.render(
            'group-navigation.html',
            user=user,
            topics=topics
        )


class BrowseMoreTopicHandler(BaseHandler):
    @catch_exception
    def get(self):
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


class CreateHandler(BaseHandler):
    def get_tags(self):
        tags = self.args.get('tags')
        tags = util.split(tags)
        for tag in tags:
            if not tag.strip():
                tags.remove(tag)
        return tags

    def notify_user(self, group_id, group_name):
        title = "创建小组"
        brief = """
            您已创建小组<a href="/g/{gid}">{name}</a>，
            系统默认指定您为该小组第一任组长。
        """.format(gid=group_id, name=group_name)
        self.muser.create_message(self.user_id, title, brief, type='1')

    @catch_exception
    @authenticated
    def post(self):
        self.get_args('name', 'intro', 'public_level', 'tags')
        self.set_arg('tags', self.get_tags())
        group_id = self.mgroup.do_create(self.user_id, **self.args)
        self.notify_user(group_id, self.args['name'])
        self.write_result(group_id)


class JoinHandler(BaseHandler):
    def notify_user(self, group_id):
        nickname = self.current_user['nickname']
        group = self.mgroup.get_group_baseinfo(group_id)
        title = "申请加入小组"
        brief = """
            <a href="/u/{nickname}">{nickname}</a>
            申请加入您的<a href="/g/{gid}">{group_name}</a>小组,
            <a href="#"> 同意 </a> | <a href="#"> 拒绝 </a>
        """.format(nickname=nickname,
                   gid=group_id,
                   group_name=group['name'])
        self.muser.create_message(group['leader_id'],
                                  title,
                                  brief,
                                  type='1',
                                  initiator=nickname)

    @catch_exception
    @authenticated
    def post(self, group_id):
        self.mgroup.join_group(group_id, self.user_id)
        self.notify_user(group_id)


class GroupHandler(BaseHandler):
    def get(self, group_id):
        group = self.mgroup.get_group_homepage(group_id)
        if group:
            self.render('group.html', group=group)
        else:
            self.render_404_page()


class GroupMemberHandler(BaseHandler):
    @catch_exception
    def get(self, group_id):
        if not self.mgroup.is_group_visiable(group_id, self.user_id):
            raise Exception('no access permission')
        page = int(self.get_argument('page', 1))
        size = int(self.get_argument('size', 20))
        members = self.mgroup.get_group_members(group_id, page, size)
        self.write_json(members)


class GroupArticleHandler(BaseHandler):
    @catch_exception
    def get(self, group_id):
        if not self.mgroup.is_group_visiable(group_id, self.user_id):
            raise Exception('no access permission')
        page = int(self.get_argument('page', 1))
        size = int(self.get_argument('size', 20))
        articles = self.mgroup.get_group_articles(group_id, page, size)
        self.write_json(articles)


class GroupSessionHistoryHandler(BaseHandler):
    @catch_exception
    def get(self, group_id):
        if not self.mgroup.is_group_visiable(group_id, self.user_id):
            raise Exception('no access permission')
        anchor_id = int(self.get_argument('anchor_id', 0))
        size = int(self.get_argument('size', 20))
        ss = self.mgroup.get_group_sessions(group_id, anchor_id, size)
        self.write_json(ss)


class TopicHandler(BaseHandler):
    @catch_exception
    def get(self, topic_id):
        topic = self.mgroup.get_topic_homepage(topic_id)
        if not self.mgroup.is_group_visiable(topic['gid'], self.user_id):
            raise Exception('no access permission')
        if topic:
            group = self.mgroup.get_group_homepage(topic['gid'])
            self.render('topic.html', group=group, topic=topic)
        else:
            self.render_404_page()


class TopicSessionHistoryHandler(BaseHandler):
    @catch_exception
    def get(self, topic_id):
        topic = self.mgroup.get_topic(topic_id)
        group_id = topic['gid']
        if not self.mgroup.is_group_visiable(group_id, self.user_id):
            raise Exception('no access permission')
        anchor_id = int(self.get_argument('anchor_id', 0))
        size = int(self.get_argument('size', 20))
        ss = self.mgroup.get_topic_sessions(topic_id, anchor_id, size)
        self.write_json(ss)


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
        reply_tid = self.get_reply_topic_id()
        if message['type'] == 'message':
            message = self.mgroup.create_group_message(
                self.group_id,
                self.user_id,
                message['content'],
                reply_tid
            )
        elif message['type'] == 'topic':
            message = self.mgroup.create_group_topic(
                self.group_id,
                self.user_id,
                message['title'],
                message['content'],
                reply_tid
            )
        if reply_tid:
            self.notify_user(reply_tid, message)
        return message

    def notify_user(self, tid, message):
        topic = self.mgroup.get_topic(tid)
        title = u"""<a href="/t/{tid}">{title}</a>""".format(
            tid=tid,
            title=topic['title'],
        )
        message_brief = util.get_abstract_str(message['content'])
        brief = u"""<a href="/t/{tid}">{message}</a>""".format(
            tid=tid,
            message=message_brief
        )
        initiator = self.current_user['nickname']
        self.muser.create_message(topic['uid'],
                                  title,
                                  brief,
                                  type='2',
                                  initiator=initiator)


    def on_message(self, message):
        self.send_message(message)


class GroupSessionAjaxHandler(GroupSessionBaseHandler):
    @catch_exception
    def get(self, group_id):
        self.channel = 'g' + str(group_id)
        self.group_id = group_id
        if not self.mgroup.is_group_visiable(self.group_id, self.user_id):
            raise Exception('no access permission')
        self.listen()

    @catch_exception
    def post(self, group_id):
        self.channel = 'g' + str(group_id)
        self.group_id = group_id
        message = self.get_argument('message')
        self.send_message(message)


class TopicSessionAjaxHandler(SessionBaseHandler):
    def get_reply_topic_id(self):
        return self.topic['tid']

    @catch_exception
    def get(self, topic_id):
        self.channel = 't' + str(topic_id)
        self.topic = self.mgroup.get_topic(topic_id)
        self.group_id = self.topic['gid']
        if not self.mgroup.is_group_visiable(self.group_id, self.user_id):
            raise Exception('no access permission')
        self.listen()

    @catch_exception
    def post(self, topic_id):
        self.channel = 't' + str(topic_id)
        self.topic = self.mgroup.get_topic(topic_id)
        self.group_id = self.topic['gid']
        message = self.get_argument('message')
        self.send_message(message)


class GroupSessionWebsocketHandler(GroupSessionBaseHandler, WebSocketHandler):
    @catch_exception
    def open(self, group_id):
        self.channel = 'g' + str(group_id)
        self.group_id = group_id
        if not self.mgroup.is_group_visiable(self.group_id, self.user_id):
            raise Exception('no access permission')
        self.listen()


class TopicSessionWebsocketHandler(GroupSessionBaseHandler, WebSocketHandler):
    def get_reply_topic_id(self):
        return self.topic['tid']

    @catch_exception
    def open(self, topic_id):
        self.channel = 't' + str(topic_id)
        self.topic = self.mgroup.get_topic(topic_id)
        self.group_id = self.topic['gid']
        if not self.mgroup.is_group_visiable(self.group_id, self.user_id):
            raise Exception('no access permission')
        self.listen()

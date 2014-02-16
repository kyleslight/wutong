#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import asynchronous
from tornado.websocket import WebSocketHandler
from tornado.escape import json_decode, json_encode
from base import BaseHandler
from lib import util


class GroupBaseHandler(BaseHandler):
    _type_table = {
        '1': 'private',
        '2': 'public',
        '3': 'publish',
    }


    @property
    def model(self):
        return self.groupmodel

    def get_group_info(self, gid):
        group_info = self.mgroup.get_group_info(gid)
        return group_info

    def get_bulletins(self, gid):
        bulletins = self.mgroup.get_bulletins(gid, 6, 0)
        return bulletins or []

    def get_member_info(self, gid, uid):
        member_info = self.mgroup.get_member_info(gid, uid)
        return member_info

    def get_group_members(self, gid):
        members = self.mgroup.get_group_members(gid, 30, 0)
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


class BrowseHandler(GroupBaseHandler):
    """
    ?tag=xxx&page=1&size=20
    ?size=20
    """
    default_size = 20

    def get(self):
        try:
            tag = self.get_argument('tag')
            page = int(self.get_argument('page', 1))
            size = int(self.get_argument('size', self.default_size))
        except ValueError:
            page = 1
            size = self.default_size

        user = self.get_current_user()
        mygroups = self.muser.get_user_groups(user['uid']) if user else []

        if tag:
            recent_group_topics = []
            recent_topics = self.mgroup.get_topics_by_tag(tag, page, size)
        else:
            if user:
                size /= 2
                recent_group_topics = self.mgroup.get_user_topics(user['uid'], 1, size)
            else:
                recent_group_topics = []
            recent_topics = self.mgroup.get_topics(1, size)

        self.render(
            'group-navigation.html',
            user=user,
            mygroups=mygroups,
            recent_group_topics=recent_group_topics,
            recent_topics=recent_topics
        )


class CreateHandler(GroupBaseHandler):
    def get_tags_from_str(self, tags):
        seps = [u' ', u';', u'；']
        tags = util.split(tags, u' ,;；')
        return tags

    def post(self):
        name = self.get_argument('name')
        intro = self.get_argument('intro')
        is_public = self.get_argument('is_public', True)
        tags = self.get_argument('tags')

        tags = self.get_tags_from_str(tags)
        if not tags:
            self.write('invalid tags')
            return

        group_id = self.mgroup.do_create(self.user_id,
                                        name,
                                        intro=intro,
                                        is_public=is_public)
        self.write(str(group_id))


class JoinHandler(GroupBaseHandler):
    def join_group(self, gid, uid):

        res = self.mgroup.do_join_group(gid, uid)
        print('-' * 80, res)
        return res

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


class MessageBaseHandler(GroupBaseHandler):
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


class GroupHandler(BaseHandler):
    def get(self, group_id):
        page = self.get_argument('page', 1)
        size = self.get_argument('size', 20)
        visiable = self.mgroup.is_group_visiable(group_id, self.user_id)

        if self.has_argument('message'):
            if not visiable:
                self.write_errmsg('no access permission')
                return
            messages = self.mgroup.get_group_sessions(group_id, page, size)
            self.write_json(messages)
        else:
            group = self.mgroup.get_group_homepage(group_id)
            if group:
                if visiable:
                    group['messages'] = self.mgroup.get_group_sessions(group_id)
                else:
                    group['messages'] = []
                self.render('group.html', group=group)
            else:
                self.render_404_page()


class TopicHandler(BaseHandler):
    def get(self, topic_id):
        page = self.get_argument('page', 1)
        size = self.get_argument('size', 20)
        visiable = self.mgroup.is_topic_visiable(topic_id, self.user_id)

        if self.has_argument('message'):
            if not visiable:
                self.write_errmsg('no access permission')
                return
            messages = self.mgroup.get_topic_sessions(topic_id, page, size)
            self.write_json(messages)
        else:
            topic = self.mgroup.get_topic_homepage(topic_id)
            if topic:
                if visiable:
                    topic['messages'] = self.mgroup.get_topic_sessions(topic_id)
                else:
                    topic['messages'] = []
                self.render('topic.html', topic=topic)
            else:
                self.render_404_page()


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

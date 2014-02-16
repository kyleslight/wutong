#!/usr/bin/env python
# -*- coding: utf-8 -*-

class GroupModel(object):

    def __init__(self, db):
        self.db = db

    def is_group_visiable(self, group_id, user_id):
        return True

    def is_topic_visiable(self, topic_id, user_id):
        return True

    def get_group_homepage(self, group_id):
        return self.calljson('get_group_homepage', group_id)

    def get_topic_homepage(self, topic_id):
        return self.calljson('get_topic_homepage', topic_id)

    def get_group_sessions(self, group_id, page, size):
        limit = size
        offset = (page - 1) * size
        messages = self.db.calljson('get_group_sessions', group_id, limit, offset)
        return messages or []

    def get_topic_sessions(self, topic_id, page, size):
        limit = size
        offset = (page - 1) * size
        messages = self.db.calljson('get_topic_sessions', topic_id, limit, offset)
        return messages or []

    def get_group_info(self, gid):
        return self.db.calljson('get_group_info', gid)

    def get_message(self, message_id):
        return self.db.calljson('get_group_message', message_id)

    def get_chat(self, chat_id):
        return self.db.calljson('get_group_chat', chat_id)

    def get_chats(self, gid, page, size):
        limit = size
        offset = (page - 1) * size
        group_chats = self.db.calljson('get_group_chats', gid, limit, offset)
        return group_chats or []

    def get_topic(self, topic_id):
        return self.db.calljson('get_topic', topic_id)

    def get_topics(self, page, size):
        limit = size
        offset = (page - 1) * size
        topics = self.db.calljson('get_topics', limit, offset)
        return topics or []

    def get_topics_by_tag(self, tag, page, size):
        limit = size
        offset = (page - 1) * size
        topics = self.db.calljson('get_topics_by_tag', tag, limit, offset)
        return topics or []

    def get_user_topics(self, uid, page, size):
        limit = size
        offset = (page - 1) * size
        topics = self.db.calljson('get_user_topics', limit, offset)
        return topics or []

    def get_group_topics(self, gid, page, size):
        limit = size
        offset = (page - 1) * size
        topics = self.db.calljson('get_group_topics', gid, limit, offset)
        return topics or []

    def get_topic_topics(self, topic_id, page, size):
        limit = size
        offset = (page - 1) * size
        topics = self.db.calljson('get_topic_topics', topic_id, limit, offset)
        return topics or []

    def get_topic_chats(self, topic_id, page, size):
        limit = size
        offset = (page - 1) * size
        chats = self.db.calljson('get_topic_chats', topic_id, limit, offset)
        return chats or []

    def get_member_info(self, gid, uid):
        return self.db.calljson('get_group_member_info', gid, uid)

    def get_group_members(self, gid, page, size):
        limit = size
        offset = (page - 1) * size
        members = self.db.calljson('get_group_members', gid, limit, offset)
        return members or []

    def get_bulletins(self, gid, page, size):
        limit = size
        offset = (page - 1) * size
        bulletins = self.db.calljson('get_group_bulletins', gid, limit, offset)
        return bulletins or []

    def join_group(self, gid, uid):
        return self.db.call('join_group', gid, uid)

    def create_group(self, uid, name, intro=None, motto=None, avatar=None, banner=None, is_public=True):
        return self.db.callfirstfield('create_group', uid, name, intro, motto, avatar, banner, is_public)

    def create_topic(self, gid, uid, title, content, reply_id=None):
        return self.db.callfirstfield('create_topic', gid, uid, title, content, reply_id)

    def create_chat(self, gid, uid, content, reply_id=None):
        return self.db.callfirstfield('create_group_chat', gid, uid, content, reply_id)

    def create_bulletin(self, gid, uid, title, content):
        return self.db.callfirstfield('create_group_bulletin', gid, uid, title, content)

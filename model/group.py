#!/usr/bin/env python
# -*- coding: utf-8 -*-

class GroupModel(object):

    def __init__(self, db):
        self.db = db

    def get_group_info(self, gid):
        select = 'SELECT get_group_info(%s)'
        group_info = self.db.getjson(select, gid)
        return group_info

    def get_message(self, message_id):
        select = 'SELECT get_group_message(%s)'
        message = self.db.getjson(select, message_id)
        return message

    def get_group_messages(self, gid, limit, offset):
        select = 'SELECT get_group_messages(%s, %s, %s)'
        messages = self.db.getjson(select, gid, limit, offset)
        return messages

    def get_topic_messages(self, tid, limit, offset):
        select = 'SELECT get_topic_messages(%s, %s, %s)'
        messages = self.db.getjson(select, tid, limit, offset)
        return messages

    def get_chats(self, gid, limit, offset):
        select = 'SELECT get_group_chats(%s, %s, %s)'
        group_chats = self.db.getjson(select, gid, limit, offset)
        return group_chats

    def get_chat(self, id):
        select = 'SELECT get_group_chat(%s)'
        chat = self.db.getjson(select, id)
        return chat

    def get_topics(self, gid, limit, offset):
        select = 'SELECT get_topics(%s, %s, %s)'
        topics = self.db.getjson(select, gid, limit, offset)
        return topics

    def get_recent_topics(self, limit, offset):
        select = 'SELECT get_recent_topics(%s, %s)'
        topics = self.db.getjson(select, limit, offset)
        return topics

    def get_user_recent_group_topics(self, uid, limit, offset):
        select = 'SELECT get_user_recent_group_topics(%s, %s, %s)'
        topics = self.db.getjson(select, uid, limit, offset)
        return topics

    def get_topic(self, topic_id):
        select = 'SELECT get_topic(%s)'
        topic = self.db.getjson(select, topic_id)
        return topic

    def get_topic_topics(self, topic_id, limit, offset):
        select = 'SELECT get_topic_topics(%s, %s, %s)'
        topics = self.db.getjson(select, topic_id, limit, offset)
        return topics

    def get_topic_chats(self, topic_id, limit, offset):
        select = 'SELECT get_topic_chats(%s, %s, %s)'
        chats = self.db.getjson(select, topic_id, limit, offset)
        return chats

    def get_member_info(self, gid, uid):
        select = 'SELECT get_group_member_info(%s, %s)'
        return self.db.getjson(select, gid, uid)

    def get_group_members(self, gid, limit, offset):
        select = 'SELECT get_group_members(%s, %s, %s)'
        return self.db.getjson(select, gid, limit, offset)

    def get_bulletins(self, gid, limit, offset):
        select = 'SELECT get_group_bulletins(%s, %s, %s)'
        bulletins = self.db.getjson(select, gid, limit, offset)
        return bulletins

    def do_create(self, uid, name, intro=None, motto=None, avatar=None, banner=None, is_public=True):
        select = 'SELECT create_group(%s, %s, %s, %s, %s, %s, %s)'
        gid = self.db.getfirstfield(select, uid, name, intro, motto, avatar, banner, is_public)
        return gid

    def do_join_group(self, gid, uid):
        select = 'SELECT join_group(%s, %s)'
        return self.db.execute(select, gid, uid)

    def do_create_topic(self, gid, uid, title, content, reply_id=None):
        select = 'SELECT create_topic(%s, %s, %s, %s, %s)'
        topic_id = self.db.getfirstfield(select, gid, uid, title, content, reply_id)
        return topic_id

    def do_create_chat(self, gid, uid, content, reply_id=None):
        select = 'SELECT create_group_chat(%s, %s, %s, %s)'
        id = self.db.getfirstfield(select, gid, uid, content, reply_id)
        return id

    def do_create_bulletin(self, gid, uid, title, content):
        select = 'SELECT create_group_bulletin(%s, %s, %s, %s)'
        return self.db.getfirstfield(select, gid, uid, title, content)

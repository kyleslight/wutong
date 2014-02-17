#!/usr/bin/env python
# -*- coding: utf-8 -*-

class GroupModel(object):

    def __init__(self, db):
        self.db = db
        self.group_map_table = {
            'private': '1',
            'public': '2',
        }

    # TODO
    def is_group_visiable(self, group_id, user_id):
        return True

    # TODO
    def is_group_member(self, group_id, user_id):
        return True

    # TODO
    def get_group_homepage(self, group_id):
        return self.db.calljson('get_group_homepage', group_id)

    # TODO
    def get_topic_homepage(self, topic_id):
        return self.db.calljson('get_topic_homepage', topic_id)

    def get_group_sessions(self, group_id, anchor_id, size):
        sessions = self.db.calljson('get_group_sessions', group_id, anchor_id, size)
        return sessions or []

    def get_topic_sessions(self, topic_id, anchor_id, size):
        sessions = self.db.calljson('get_topic_sessions', topic_id, anchor_id, size)
        return sessions or []

    def get_mygroup_topics(self, user_id, page, size):
        limit = size
        offset = (page - 1) * size
        topics = self.db.calljson('get_mygroup_topics', user_id, limit, offset)
        return topics or []

    def get_topics(self, page, size):
        limit = size
        offset = (page - 1) * size
        topics = self.db.calljson('get_topics', limit, offset)
        return topics or []

    def get_user_groups(self, user_id, page, size):
        limit = size
        offset = (page - 1) * size
        topics = self.db.calljson('get_user_groups', user_id, limit, offset)
        return topics or []

    def do_create(self, user_id, name, intro, public_level, **kwargs):
        public_level = self.group_map_table.get(public_level)
        if not public_level:
            raise Exception('error public level')
        group_id = self.db.callfirstfield('create_group', user_id, name, intro, public_level)
        if not group_id > 0:
            raise Exception('create group failed')
        tags = kwargs.get('tags')
        self.db.call('update_group_tags', group_id, tags)
        return group_id

    def join_group(self, group_id, user_id):
        errno = self.db.callfirstfield('join_group', group_id, user_id)
        if errno == 0:
            return
        elif errno == 1:
            raise Exception('already post')
        elif errno == 2:
            raise Exception('already joined')
        else:
            raise Exception('unknow error')

    def create_group_message(self, group_id, user_id, content, topic_id=None):
        msg = self.db.calljson('create_group_message',
                               group_id,
                               user_id,
                               content,
                               topic_id)
        if not msg:
            raise Exception('create group message error')
        return msg

    def create_group_topic(self, group_id, user_id, title, content, topic_id=None):
        msg = self.db.calljson('create_group_topic',
                               group_id,
                               user_id,
                               title,
                               content,
                               topic_id)
        if not msg:
            raise Exception('create group topic error')
        return msg

    # TODO
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

    def create_topic(self, gid, uid, title, content, reply_id=None):
        return self.db.callfirstfield('create_topic', gid, uid, title, content, reply_id)

    def create_chat(self, gid, uid, content, reply_id=None):
        return self.db.callfirstfield('create_group_chat', gid, uid, content, reply_id)

    def create_bulletin(self, gid, uid, title, content):
        return self.db.callfirstfield('create_group_bulletin', gid, uid, title, content)

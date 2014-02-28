#!/usr/bin/env python
# -*- coding: utf-8 -*-

class GroupModel(object):
    def __init__(self, db):
        self.db = db
        self.group_map_table = {
            'private': '1',
            'public': '2',
        }

    def is_group_visiable(self, group_id, user_id):
        return self.db.callfirstfield('is_group_visiable', group_id, user_id)

    def is_group_member(self, group_id, user_id):
        return self.db.callfirstfield('is_group_member', group_id, user_id)

    def get_group_baseinfo(self, group_id):
        return self.db.calljson('get_group_baseinfo', group_id)

    def get_group_homepage(self, group_id):
        return self.db.calljson('get_group_homepage', group_id)

    def get_topic_homepage(self, topic_id):
        return self.db.calljson('get_topic_homepage', topic_id)

    def get_group_members(self, group_id, page, size):
        limit = size
        offset = (page - 1) * size
        members = self.db.calljson('get_group_members', group_id, limit, offset)
        return members or []

    def get_group_articles(self, group_id, page, size):
        limit = size
        offset = (page - 1) * size
        articles = self.db.calljson('get_group_articles', group_id, limit, offset)
        return articles or []

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

    def get_browse_topics(self, page, size):
        limit = size
        offset = (page - 1) * size
        topics = self.db.calljson('get_browse_topics', limit, offset)
        return topics or []

    def get_topic(self, topic_id):
        return self.db.calljson('get_topic', topic_id)

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

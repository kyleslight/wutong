#!/usr/bin/env python
# -*- coding: utf-8 -*-


class SearchModel(object):
    def __init__(self, db):
        self.db = db

    def get_article_item(self, article_id):
        item = self.db.calljson('get_article_search_item', article_id)
        return item

    def get_group_item(self, group_id):
        item = self.db.calljson('get_group_search_item', group_id)
        return item

    def get_user_item(self, user_id):
        item = self.db.calljson('get_user_search_item', user_id)
        return item

    def get_topic_item(self, topic_id):
        item = self.db.calljson('get_topic_search_item', topic_id)
        return item

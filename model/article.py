#!/usr/bin/env python
# -*- coding: utf-8 -*-


class ArticleModel(object):
    def __init__(self, db):
        self.db = db
        self.article_map_table = {
            'draft': '1',
            'private': '2',
            'public': '3',
            'publish': '4',
        }

    def do_create(self, user_id, title, mainbody, public_level, **kwargs):
        public_level = self.article_map_table.get(public_level)
        if not public_level:
            raise Exception('error public level')
        article_id = self.db.callfirstfield(
            'create_article',
            user_id, title, mainbody,
            kwargs.get('intro'),
            kwargs.get('suit_for'),
            kwargs.get('refers'),
            kwargs.get('series'),
            kwargs.get('resources'),
            public_level
        )
        if not article_id > 0:
            raise Exception('create article failed')
        tags = kwargs.get('tags')
        coeditors = kwargs.get('coeditors')
        self.db.call('update_article_tags', article_id, tags)
        self.db.call('update_article_coeditors', article_id, coeditors)
        return article_id

    def do_update(self, article_id, user_id, title, mainbody, **kwargs):
        public_level = kwargs.get('public_level')
        public_level = self.article_map_table[public_level]
        article_id = self.db.update(
            'article',
            user_id, title, mainbody,
            kwargs.get('intro'),
            kwargs.get('suit_for'),
            kwargs.get('refers'),
            kwargs.get('series'),
            kwargs.get('resources'),
            public_level
        )
        if not article_id > 0:
            raise Exception('create article failed')
        tags = kwargs.get('tags')
        coeditors = kwargs.get('coeditors')
        self.db.call('update_article_tags', article_id, tags)
        self.db.call('update_article_coeditors', article_id, coeditors)
        return article_id

    def get_article(self, article_id):
        article = self.db.calljson('get_article', article_id)
        return article

    def get_articles(self, page, size, tag=None):
        limit = size
        offset = (page - 1) * size
        articles = self.db.calljson('get_articles', limit, offset, tag)
        return articles or []

    def get_bottom_comments(self, article_id, page, size, **kwargs):
        limit = size
        offset = (page - 1) * size
        comments = self.db.calljson('get_bottom_comments', article_id, limit, offset)
        return comments or []

    def get_side_comments(self, article_id, **kwargs):
        comments = self.db.calljson('get_side_comments', aritcle_id)
        return comments or []

    def create_bottom_comment(self, article_id, user_id, content, **kwargs):
        comment = self.db.calljson('create_bottom_comment',
                                   article_id, user_id, content,
                                   kwargs.get('reply_id'))
        if not comment:
            raise Exception('create bottom comment failed')
        return comment

    def create_side_comment(self, article_id, user_id, content, paragraph_id, **kwargs):
        comment = self.db.calljson('create_side_comment',
                                   article_id, user_id, content,
                                   paragraph_id)
        if not comment:
            raise Exception('create side comment failed')
        return comment

    def delete_bottom_comment(self, user_id, comment_id):
        res = self.delete('article_bottom_comment', where='uid=%s and id=%s', wherevalues=[user_id, comment_id])
        if not res:
            raise Exception('delete bottom comment failed')

    def delete_side_comment(self, user_id, comment_id):
        res = self.delete('article_side_comment', where='uid=%s and id=%s', wherevalues=[user_id, comment_id])
        if not res:
            raise Exception('delete side comment failed')

    def create_article_view(self, article_id, user_id, ip):
        return self.db.call('create_article_view', article_id, user_id, ip)

    def get_article_interaction(self, article_id):
        info = self.db.calljson('get_article_interaction', article_id)
        for key in info:
            if not info[key]:
                info[key] = 0
        return info

    def get_myinteraction_info(self, article_id, user_id):
        info = self.db.calljson('get_myinteraction_info', article_id, user_id)
        if not info:
            raise Exception('no interaction')

    def update_myinteraction_info(self, article_id, user_id, action, value=None):
        map_table = {
            'score': 'article_score',
            'collect': 'article_collection',
            'forward': 'article_forwarded',
        }

        table_name = map_table[action]
        if not self.db.call('update_myinteraction_info', article_id, user_id, value, table_name):
            raise Exception('update interaction failed')

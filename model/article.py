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
        res = self.db.update(
            'article',
            {
                'uid': user_id,
                'title': title,
                'mainbody': mainbody,
                'intro': kwargs.get('intro'),
                'suit_for': kwargs.get('suit_for'),
                'refers': kwargs.get('refers'),
                'series': kwargs.get('series'),
                'resources': kwargs.get('resources'),
                'public_level': public_level,
            },
            where='aid=%s',
            wherevalues=[article_id]
        )
        if not res > 0:
            raise Exception('create article failed')
        tags = kwargs.get('tags')
        coeditors = kwargs.get('coeditors')
        self.db.call('update_article_tags', article_id, tags)
        self.db.call('update_article_coeditors', article_id, coeditors)
        return res

    def is_article_author(self, article_id, user_id):
        return self.db.callfirstfield('is_article_author', article_id, user_id)

    def get_article_baseinfo(self, article_id):
        article = self.db.calljson('get_article_baseinfo', article_id)
        return article

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
        comments = self.db.calljson('get_side_comments', article_id)
        return comments or []

    def create_bottom_comment(self, article_id, user_id, content, **kwargs):
        comment_id = self.db.callfirstfield('create_bottom_comment',
                                            article_id, user_id, content,
                                            kwargs.get('reply_id'))
        if not comment_id:
            raise Exception('create bottom comment failed')
        comment = self.db.calljson('get_bottom_comment', comment_id)
        return comment

    def create_side_comment(self, article_id, user_id, content, paragraph_id, **kwargs):
        comment_id = self.db.callfirstfield('create_side_comment',
                                            article_id, user_id, content,
                                            paragraph_id)
        if not comment_id:
            raise Exception('create side comment failed')
        comment = self.db.calljson('get_side_comment', comment_id)
        return comment

    def delete_bottom_comment(self, comment_id, user_id):
        res = self.delete('article_bottom_comment', where='uid=%s and id=%s', wherevalues=[user_id, comment_id])
        if not res:
            raise Exception('delete bottom comment failed')

    def delete_side_comment(self, comment_id, user_id):
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
        return info

    def update_article_myscore(self, article_id, user_id, score):
        if not self.db.call('update_article_myscore', article_id, user_id, score):
            raise Exception('score failed')

    def create_article_myforward(self, article_id, user_id):
        # 转发行为和评分不一样, 转发成功但没写进数据库也是允许的
        self.db.insert('article_forwarded', {
            'aid': article_id,
            'uid': user_id
        })

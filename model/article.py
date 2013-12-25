#!/usr/bin/env python
# -*- coding: utf-8 -*-


class ArticleModel(object):

    def __init__(self, db):
        self.db = db

    def get_article_info(self, aid):
        select = 'SELECT get_article_info(%s)'
        article_info = self.db.getjson(select, aid)
        return article_info

    def get_article_list(self, sort, limit, offset):
        select = 'SELECT get_article_list(%s, %s, %s)'
        article_list = self.db.getjson(select, sort, limit, offset)
        return article_list

    def get_comment(self, comment_id):
        select = 'SELECT get_comment(%s)'
        comment = self.db.getjson(select, comment_id)
        return comment

    def get_side_comments(self, aid):
        select = 'SELECT get_side_comments(%s)'
        comments = self.db.getjson(select, aid)
        return comments

    def get_bottom_comments(self, aid, limit=30, offset=0):
        select = 'SELECT get_bottom_comments(%s, %s, %s)'
        comments = self.db.getjson(select, aid, limit, offset)
        return comments

    def do_create(self, uid, title, mainbody, subtitle=None,
                  description=None, suit_for=None, reference=None,
                  series=None, resource=None, is_public=u'推送'):
        select = 'SELECT create_article(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        aid = self.db.getfirstfield(select, uid, title, mainbody, subtitle,
                                    description, suit_for, reference,
                                    series, resource, is_public)
        return aid

    def create_side_comment(self, aid, uid, content, paragraph_id):
        select = 'SELECT create_side_comment(%s, %s, %s, %s)'
        comment_id = self.db.getfirstfield(select,
                                           aid,
                                           uid,
                                           content,
                                           paragraph_id)
        return comment_id

    def create_bottom_comment(self, aid, uid, content):
        select = 'SELECT create_bottom_comment(%s, %s, %s)'
        comment_id = self.db.getfirstfield(select,
                                           aid,
                                           uid,
                                           content)
        return comment_id

    def create_article_tags(self, aid, tags):
        insert = '''insert into article
                                (aid, tag_name)
                    values (%s, %s)
                     where not (aid = %s and tag_name = %s)'''
        for tag in tags:
            self.db.execute(insert, aid, tag)

    def remove_article_tags(self, aid):
        pass

    def get_article_tags(self, aid):
        pass

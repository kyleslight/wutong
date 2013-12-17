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

    def do_create(self, uid, title, mainbody, subtitle=None,
                  description=None, suit_for=None, reference=None,
                  series=None, resource=None, is_public=u'推送'):
        select = 'SELECT create_article(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        aid = self.db.getfirstfield(select, uid, title, mainbody, subtitle,
                                    description, suit_for, reference,
                                    series, resource, is_public)
        return aid

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import authenticated
from base import BaseHandler


class ArticleBaseHandler(BaseHandler):
    @property
    def model(self):
        return self.articlemodel

    def create_article(self, title, mainbody, subtitle=None,
                       description=None, suit_for=None, reference=None,
                       partner=None, tags=None):
        article_id =  self.model.do_create(self.user_id, title, mainbody, subtitle,
                                           description, suit_for, reference)
        return article_id


class BrowseArticleHandler(ArticleBaseHandler):
    def get_article_list(self, sort, page_id=0):
        article_list = self.model.get_article_list(sort, 30, page_id)
        return article_list or []

    def get(self, sort=None):
        article_list = self.get_article_list(sort, 0)
        self.render('browse.html', article_list=article_list)


class OpusHandler(ArticleBaseHandler):
    def get(self, article_id):
        self.render('opus.html')


class CreateArticleHandler(ArticleBaseHandler):
    def get(self):
        self.render('create.html')

    def post(self):
        title = self.get_argument('title')
        mainbody = self.get_argument('textArea')
        subtitle = self.get_argument('subtitle')
        description = self.get_argument('describe')
        suit_for = self.get_argument('suit')
        reference = self.get_argument('reference')

        # article_user
        partner = self.get_argument('partner')
        tags = self.get_argument('tags')
        article_id = self.create_article(title, mainbody, subtitle, description,
                                         suit_for, reference, partner, tags)
        self.redirect('/a/%s' % article_id)


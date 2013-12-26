#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import authenticated
from tornado.escape import json_encode, json_decode
from base import BaseHandler
import re


class ArticleBaseHandler(BaseHandler):
    @property
    def model(self):
        return self.articlemodel

    def create_article(self,
                       title,
                       mainbody,
                       subtitle=None,
                       description=None,
                       suit_for=None,
                       reference=None,
                       partner=None,
                       tags=[]):
        article_id =  self.model.do_create(self.user_id,
                                           title,
                                           mainbody,
                                           subtitle,
                                           description,
                                           suit_for,
                                           reference)
        self.model.create_article_tags(article_id, tags)
        return article_id


class BrowseArticleHandler(ArticleBaseHandler):
    def get_article_list(self, sort, page_id=0):
        article_list = self.model.get_article_list(sort, 30, page_id)
        return article_list or []

    def get(self, sort=None):
        article_list = self.get_article_list(sort, 0)
        self.render('browse.html', article_list=article_list)


class OpusHandler(ArticleBaseHandler):
    def get_article(self, article_id):
        article = self.model.get_article_info(article_id)
        self.model.add_article_view(article_id, self.user_id)
        return article

    def get(self, article_id):
        article = self.get_article(article_id)
        self.render('opus.html', article=article)


class CreateArticleHandler(ArticleBaseHandler):
    def has_top_tag(self, tags):
        pass

    def get(self):
        self.render('create.html')

    def post(self):
        if not self.get_current_user():
            self.write('not login')
            return
        title = self.get_argument('title')
        mainbody = self.get_argument('textArea')
        subtitle = self.get_argument('subtitle')
        description = self.get_argument('describe')
        suit_for = self.get_argument('suit')
        reference = self.get_argument('reference')
        partner = self.get_argument('partner')
        tags = self.get_argument('tags').split(';')
        if not self.has_top_tag(tags):
            self.write('no tag')
            return

        article_id = self.create_article(title,
                                         mainbody,
                                         subtitle,
                                         description,
                                         suit_for,
                                         reference,
                                         partner,
                                         tags)
        self.redirect('/a/%s' % article_id)


class CommentBaseHandler(ArticleBaseHandler):
    def get_comments(self, article_id):
        pass

    def create_comment(self, article_id, content):
        pass

    def render_comment(self, comment, **kwargs):
        pass

    def get(self, article_id):
        article_id = int(article_id)
        comments = self.get_comments(article_id)
        after_render = []
        for comment in comments:
            comment = self.render_comment(comment)
            after_render.append(comment)
        self.write(json_encode(after_render))

    @authenticated
    def post(self, article_id):
        article_id = int(article_id)
        content = self.get_argument('content')
        comment = self.create_comment(article_id, content)
        if comment:
            self.write(self.render_comment(comment))
        else:
            self.write('failed')


class SideCommentHandler(CommentBaseHandler):
    def get_comments(self, article_id):
        comments = self.model.get_side_comments(article_id)
        return comments

    def create_comment(self, article_id, content):
        paragraph_id = self.get_argument('paragraph_id')
        comment_id = self.model.create_side_comment(
            article_id,
            self.user_id,
            content,
            paragraph_id
        )
        comment = self.model.get_comment(comment_id)
        return comment

    def render_comment(self, comment):
        res = self.render_module_string('side_comment.html', comment=comment)
        return res


class BottomCommentHandler(CommentBaseHandler):
    def get_comments(self, article_id):
        limit = 20
        page_id = self.get_argument('page_id', 0)
        comments = self.model.get_bottom_comments(article_id, limit, page_id)
        return comments

    def create_comment(self, article_id, content):
        comment_id = self.model.create_bottom_comment(
            article_id,
            self.user_id,
            content
        )
        comment = self.model.get_comment(comment_id)
        return comment

    def render_comment(self, comment):
        res = self.render_module_string('bottom_comment.html', comment=comment)
        return res

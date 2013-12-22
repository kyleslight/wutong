#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import authenticated
from base import BaseHandler
from tornado.escape import json_decode, json_encode


class ArticleBaseHandler(BaseHandler):
    @property
    def model(self):
        return self.articlemodel

    def create_article(self, title, mainbody, subtitle=None,
                       description=None, suit_for=None, reference=None,
                       partner=None, tags=None):
        article_id =  self.model.do_create(self.user_id,
                                           title,
                                           mainbody,
                                           subtitle,
                                           description,
                                           suit_for,
                                           reference)
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
        return article

    def get(self, article_id):
        article = self.get_article(article_id)
        self.render('opus.html', article=article)


class CreateArticleHandler(ArticleBaseHandler):
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

        # article_user
        partner = self.get_argument('partner')
        tags = self.get_argument('tags')
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

    def render_comments(self, comments, **kwargs):
        pass

    def get(self, article_id):
        article_id = int(article_id)
        comments = self.get_comments(article_id)
        comments = self.render_comments(comments)
        self.write(comments)

    @authenticated
    def post(self, article_id):
        article_id = int(article_id)
        content = self.get_argument('content')
        comment_id = self.create_comment(article_id, content)
        if comment_id:
            self.write('success')
        else:
            self.write('failed')


class SideCommentHandler(CommentBaseHandler):
    def get_comments(self, article_id):
        comments = self.model.get_side_comments(article_id)
        return comments

    def create_comment(self, article_id, content):
        paragraph_id = self.get_argument('paragraph_id')
        comment_id = self.model.create_side_comment(article_id,
                                                    self.user_id,
                                                    content,
                                                    paragraph_id)
        return comment_id

    def render_comments(self, comments):
        return json_encode(comments)


class BottomCommentHandler(CommentBaseHandler):
    def get_comments(self, article_id):
        limit = 20
        page_id = self.get_argument('page_id', 0)
        comments = self.model.get_bottom_comments(article_id, limit, page_id)
        return comments

    def create_comment(self, article_id, content):
        comment_id = self.model.create_bottom_comment(article_id,
                                                      self.user_id,
                                                      content)
        return comment_id

    def render_comments(self, comments):
        renders = []
        for comment in comments:
            res = self.render_module_string('bottom_comment.html',
                                            comment=comment)
            renders.append(res)
        return ''.join(renders)

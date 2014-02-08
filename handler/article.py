#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import authenticated
from tornado.escape import json_encode, json_decode
from base import BaseHandler
from lib import util


class ArticleBaseHandler(BaseHandler):
    @property
    def model(self):
        return self.articlemodel

    def create_article(self, title, mainbody, tags=[], **kwargs):
        article_id =  self.model.do_create(
            self.user_id,
            title, mainbody,
            tags, **kwargs
        )
        return article_id


class BrowseHandler(ArticleBaseHandler):
    def get(self, sort=None):
        # try:
        #     tag = self.get_argument('tag')
        #     page = int(self.get_argument('page', 1))
        #     size = int(self.get_argument('size', 20))
        # except ValueError:
        #     page = 1
        #     size = 20

        # if tag:
        #     articles = self.model.get_articles_by_tag(tag, page, size)
        # else:
        #     articles = self.model.get_articles(page, size)
        self.render('browse.html', article_list=[])


class OpusHandler(ArticleBaseHandler):
    def get_article(self, article_id):
        ip = self.request.remote_ip
        article = self.model.get_article_info(article_id)
        self.model.create_article_view(article_id, self.user_id, ip)
        return article

    def get(self, article_id):
        article = self.get_article(article_id)
        if article:
            user = self.get_current_user()
            self.render('opus.html', article=article, user=user)
        else:
            self.write_error(404)


class CreateHandler(ArticleBaseHandler):
    top_tags = {
        u'文章': set([
            u'学科', u'技术', u'教程', u'文学',
            u'发现', u'日常', u'随笔', u'娱乐',
            u'杂',
        ]),
        u'片段': set([
            u'问答', u'idea', u'状态', u'心情',
            u'推荐', u'语录', u'段子', u'周边',
            u'杂',
        ]),
        u'摄影': set([
            u'人像', u'风光', u'纪实', u'静物',
            u'动物', u'建筑', u'生态', u'游记',
            u'杂',
        ]),
        u'绘画': set([
            u'手绘', u'故事', u'CG', u'水彩',
            u'纹案', u'建筑', u'平面', u'概念',
            u'杂',
        ]),
        u'项目': set([
            u'Web', u'Android', u'iOS', u'Linux',
            u'Mac OS', u'Windows', u'平面', u'原型',
            u'杂',
        ]),
    }

    def get_tags_from_str(self, tags):
        tags = util.split(tags)

        # have any top tag ?
        top_tags = set()
        map(top_tags.update, self.top_tags.values())
        for tag in tags:
            if tag in top_tags:
                return tags
        return None

    def get(self):
        self.render('create.html')

    def post(self):
        if not self.get_current_user():
            self.write('not login')
            return

        opus_type = self.get_argument('type')
        title = self.get_argument('title')
        mainbody = self.get_argument('textArea')
        tags = self.get_argument('tags')
        is_public = int(self.get_argument('is_public') == 'true')
        is_public += int(self.get_argument('push') == 'true')
        kwargs = dict(
            description=self.get_argument('describe'),
            suit_for=self.get_argument('suit'),
            reference=self.get_argument('reference'),
            series=self.get_argument('series'),
            resource=self.get_argument('resource'),
            partner=self.get_argument('cooperation'),
            is_public=is_public,
        )

        tags = self.get_tags_from_str(tags)
        if not tags:
            self.write('invalid tags')
            return

        article_id = self.create_article(title, mainbody, tags, **kwargs)
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


class ArticleScoreHandler(ArticleBaseHandler):
    def get_score(self, article_id):
        return self.model.get_article_score(article_id, self.user_id)

    def create_or_update_score(self, article_id, score):
        if self.get_score(article_id):
            return self.model.update_article_score(article_id, self.user_id, score)
        else:
            return self.model.create_article_score(article_id, self.user_id, score)

    @authenticated
    def get(self, article_id):
        score = self.get_score(article_id)
        self.write(str(score))

    @authenticated
    def post(self, article_id):
        article_id = int(article_id)
        score = int(self.get_argument('score'))
        if not (1 <= score <= 10):
            self.write('out range')
        if not self.create_or_update_score(article_id, score):
            self.write('failed')


class ArticleCollectionHandler(ArticleBaseHandler):
    def is_collected(self, article_id):
        return self.model.is_article_collected(article_id, self.user_id)

    def create_or_delete_collection(self, article_id):
        if self.is_collected(article_id):
            return self.model.delete_article_collection(article_id, self.user_id)
        else:
            return self.model.create_article_collection(article_id, self.user_id)

    @authenticated
    def get(self, article_id):
        state = self.is_collected(article_id)
        self.write(state)

    @authenticated
    def post(self, article_id):
        article_id = int(article_id)
        if not self.create_or_delete_collection(article_id):
            self.write('failed')

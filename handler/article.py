#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import authenticated
from tornado.escape import json_encode, json_decode
from base import BaseHandler
from lib import util


class BrowseHandler(BaseHandler):
    def get(self):
        try:
            tag = self.get_argument('tag')
            page = int(self.get_argument('page', 1))
            size = int(self.get_argument('size', 20))
            articles = self.marticle.get_articles(page, size, tag=tag)
            if self.get_argument('datatype') == 'json':
                self.write_json(articles)
            else:
                self.render('browse.html', articles=articles)
        except Exception as e:
            self.write_error(403)


class EditBaseHandler(BaseHandler):
    def get(self):
        # 需要检查用户登录状态, 但由于使用ajax, 所以由前端进行检查
        self.render('edit.html')

    def get_article_args(self):
        self.get_args('title', 'textArea', 'tags',
                      'type', 'describe', 'suit',
                      'reference', 'series', 'resource',
                      'is_public', 'push', 'cooperation',
                      textArea='mainbody',
                      describe='intro',
                      suit='suit_for',
                      reference='refers',
                      resource='resources',
                      push='is_push',
                      cooperation='coeditors')
        self.check_arg('type', self.is_opus_type)
        self.set_arg('tags', self.get_tags())
        self.set_arg('refers', self.get_refers())
        self.set_arg('resources', self.get_resources())
        self.set_arg('coeditors', self.get_coeditors())
        if not self.args['intro']:
            abstract_text = util.html2text(self.args['mainbody'])
            abstract_text = util.get_abstract_str(abstract_text, 100)
            self.set_arg('intro', abstract_text)
        if self.has_argument('draft'):
            self.args['public_level'] = 'draft'
        else:
            self.check_arg('is_public', util.is_bool)
            self.check_arg('is_push', util.is_bool)
            self.args['public_level'] = self.get_public_level()
        return self.args

    def is_opus_type(self, value):
        # TODO
        return True

    def get_tags(self):
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

        tags = self.args.get('tags')
        tags = util.split(tags)
        # TODO
        if self.settings['debug']:
            top_tags = {'debug': tags}
        # have any top tag ?
        tmp = set()
        [tmp.update(t) for t in top_tags.values()]
        for tag in tags:
            if tag in tmp:
                return tags
        raise Exception('no top tag')

    def get_refers(self):
        refers = self.args.get('refers')
        if refers is None:
            refers = ''
        refers = util.split(refers)
        return refers

    def get_resources(self):
        resources = self.args.get('resources')
        if resources is None:
            resources = ''
        resources = util.split(resources)
        return resources

    def get_coeditors(self):
        coeditors = self.args.get('coeditors')
        if coeditors is None:
            coeditors = ''
        coeditors = util.split(coeditors)
        return coeditors

    def get_public_level(self):
        is_public = util.get_bool(self.args.get('is_public'))
        is_push = util.get_bool(self.args.get('is_push'))
        if not is_public:
            return 'private'
        elif not is_push:
            return 'public'
        elif is_push:
            return 'publish'


class UpdateHandler(EditBaseHandler):
    def get(self, article_id):
        try:
            if self.get_argument('datatype') == 'json':
                if self.marticle.is_article_author(article_id, self.user_id):
                    article = self.marticle.get_article(article_id)
                    self.write_json(article)
                else:
                    raise Exception('no access permission')
            else:
                self.render('edit.html')
        except Exception as e:
            self.write_error(403)

    @authenticated
    def post(self, article_id):
        try:
            self.get_article_args()
            article = self.marticle.get_article(article_id)
            self.marticle.do_update(article_id, self.user_id, **self.args)
        except Exception as e:
            self.write_errmsg(e)


class CreateHandler(EditBaseHandler):
    @authenticated
    def post(self):
        try:
            self.get_article_args()
            article_id = self.marticle.do_create(self.user_id, **self.args)
        except Exception as e:
            self.write_errmsg(e)
            return
        self.redirect('/a/%s' % article_id)


class ArticleHandler(BaseHandler):
    def get(self, article_id):
        try:
            article = self.marticle.get_article(article_id)
            editable = self.user_id == article.get('uid')
            if not article or (article['public_level'] < '3' and not editable):
                self.render_404_page()
                return
            article['editable'] = editable
            article['logined'] = True if self.user_id else False
            self.marticle.create_article_view(article_id, self.user_id, self.ip)
            info = self.marticle.get_article_interaction(article_id)
            article.update(info)
            self.render('article.html', article=article)
        except Exception as e:
            self.write_errmsg(e)


class CommentHandler(BaseHandler):
    def get(self, article_id):
        try:
            self.article_id = article_id
            comment_type = self.get_argument('type')
            page = int(self.get_argument('page', 1))
            size = int(self.get_argument('size', 20))
            comments = self.call_by_type('get_%s_comments', page=1, size=20)
            self.write_json(comments)
        except Exception as e:
            self.write_errmsg(e)

    @authenticated
    def post(self, article_id):
        try:
            self.article_id = article_id
            if self.has_argument('delete'):
                self.do_delete()
            else:
                self.do_create()
        except Exception as e:
            self.write_errmsg(e)

    def do_create(self):
        content = self.get_argument('content')
        reply_id = self.get_argument('reply_id')
        comment_type = self.get_argument('type')

        if not reply_id:
            reply_id = None
        self.check_content(content)
        if comment_type == 'bottom':
            comment = self.marticle.create_bottom_comment(
                self.user_id,
                self.article_id,
                content,
                reply_id=reply_id,
            )
        elif comment_type == 'side':
            paragraph_id = self.get_argument('paragraph_id')
            comment = self.marticle.create_side_comment(
                self.user_id,
                self.article_id,
                content,
                reply_id=reply_id,
                paragraph_id=paragraph_id
            )
        else:
            raise Exception('invalid comment type')
        self.write_json(comment)

    def do_delete(self):
        q>'do_delete'
        comment_id = self.get_argument('id')
        comment_type = self.get_argument('type')

        if comment_type == 'bottom':
            self.delete_bottom_comment(self.user_id, comment_id)
        elif comment_type == 'side':
            self.delete_side_comment(self.user_id, comment_id)
        else:
            raise Exception('invalid comment type')

    def check_comment_type(self, value):
        if value not in ('bottom', 'side'):
            raise Exception('unknow comment type')

    def check_content(self, value):
        value = value.strip()
        if not value:
            raise Exception('input not empty')


class InteractHandler(BaseHandler):
    @authenticated
    def get(self, article_id):
        try:
            info = self.marticle.get_myinteraction_info(article_id, self.user_id)
            self.write_json(info)
        except Exception as e:
            self.write_errmsg(e)

    def post(self, article_id):
        try:
            if self.has_argument('score'):
                score = int(self.get_arg('score'))
                self.check_arg('score', lambda x: 1 <= int(x) <= 10)
                self.marticle.update_article_myscore(article_id, self.user_id, score)
            elif self.has_argument('collect'):
                self.muser.update_collection(self.user_id, '1', article_id)
            elif self.has_argument('forward'):
                self.marticle.create_article_myforward(article_id, self.user_id)
        except Exception as e:
            self.write_errmsg(e)

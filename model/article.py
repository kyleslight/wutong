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

    def do_create(self,
                  uid,
                  title, mainbody,
                  tags=[],
                  description=None,
                  suit_for=None,
                  reference=None,
                  series=None,
                  resource=None,
                  is_public=2,
                  partner=None,
                  **kwargs):
        select = 'SELECT create_article(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        aid = self.db.getfirstfield(select,
                                    uid,
                                    title,
                                    mainbody,
                                    description,
                                    suit_for,
                                    reference,
                                    series,
                                    resource,
                                    is_public)
        self.create_article_tags(aid, tags)
        # self.add_article_partner(aid, partner)
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
        insert = 'SELECT create_article_tags(%s, %s)'
        return self.db.execute(insert, aid, (tags, ))

    def remove_article_tags(self, aid):
        delete = 'delete from article_tag where aid = %s'
        return self.db.execute(delete, aid)

    def get_article_tags(self, aid):
        select = 'SELECT get_article_tags(%s)'
        return self.db.getjson(select, aid)

    def get_article_score(self, aid, uid):
        select = 'select score from article_score where aid = %s and uid = %s'
        return self.db.getfirstfield(select, aid, uid)

    def is_article_collected(self, aid, uid):
        select = 'select id from article_collection where aid = %s and uid = %s'
        result = self.db.getfirstfield(select, aid, uid)
        return True if result else False

    def create_article_view(self, aid, uid=None, ip=None):
        select = 'SELECT create_article_view(%s, %s, %s)'
        return self.db.execute(select, aid, uid, ip)

    def update_article_score(self, aid, uid, score):
        where = 'aid = %s and uid = %s'
        wherevalues = (aid, uid)
        return self.db.update(
            'article_score',
            {
                'score': score
            },
            where=where,
            wherevalues=wherevalues
        )

    def create_article_score(self, aid, uid, score):
        return self.db.callfirstfield('create_article_score', aid, uid, score)

    def create_article_collection(self, aid, uid):
        return self.db.callfirstfield('create_article_collection', aid, uid)

    def delete_article_collection(self, aid, uid):
        where = 'aid = %s and uid = %s'
        wherevalues = (aid, uid)
        return self.db.delete(
            'article_collection',
            where=where,
            wherevalues=wherevalues
        )

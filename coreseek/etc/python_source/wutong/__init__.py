#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import psycopg2

dsn = "dbname=%s user=%s password=%s host=%s port=%s" % (
    os.getenv("WUTONG_DB", "wutong_test"),
    os.getenv("WUTONG_DB_USER", "wutong"),
    os.getenv("WUTONG_DB_PASSWD", "wutong"),
    os.getenv("WUTONG_DB_HOST", "localhost"),
    os.getenv("WUTONG_DB_PORT", '5432')
)

class BaseSource(object):
    def __init__(self, conf):
        self.conf = conf
        self._row_count = None

    def GetScheme(self):
        """
        返回所有需要被索引的字段的属性
        """
        return [
            # ('id' , {'docid':True, } ),
            # ('subject', { 'type':'text'} ),
            # ('context', { 'type':'text'} ),
            # ('author_id', {'type':'integer'} ),
        ]

    def GetFieldOrder(self):
        """
        全文字段被检索的顺序
        """
        return [
            # ('subject', 'context')
        ]

    def Connected(self):
        """
        获取数据前的连接处理, 一般用于进行数据库的连接等预处理
        """
        try:
            self.cnn = psycopg2.connect(dsn=dsn)
            self.cur = self.cnn.cursor()
        except:
            return False
        return True

    def OnBeforeIndex(self):
        """
        数据获取前处理, 类似sql_query_pre配置选项的作用
        """
        self.sql = None
        self.sql_args = None
        raise NotImplementedError

    def NextDocument(self, *args):
        """
        文档获取处理, 获取实际的需要参与检索的数据, 按条获取,
        需要获取的字段, 作为self自身的属性给出,
        相当于sql_query的作用, 每次读取一条数据
        `args[0]`是`csfHelper.HitCollector`对象
        """
        if self._row_count is None:
            try:
                self.cur.execute(self.sql, self.sql_args)
                self._row_count = self.cur.rowcount
            except psycopg2.IntegrityError as err:
                logging.error("[%s]%s", err.pgcode, err)
            except Exception as e:
                logging.error(e)
            self.cnn.commit()
        return self._getRow()

    def OnAfterIndex(self):
        """
        数据获取后处理, 类似sql_query_post配置选项的作用
        """
        return True or False

    def OnIndexFinished(self):
        """
        索引完成时处理, 类似sql_query_post_index配置选项的作用
        """
        self.cur.close()
        self.cnn.close()
        return True or False

    def _getRow(self):
        raise NotImplementedError


class ArticleSource(BaseSource):
    def GetScheme(self):
        return [
            ('aid', {'docid': True}),
            ('title', {'type': 'text'}),
            ('intro', {'type': 'text'}),
            ('mainbody', {'type': 'text'}),
            ('author', {'type': 'text'}),
        ]

    def GetFieldOrder(self):
        return [
            ('title', 'intro', 'author', 'mainbody')
        ]

    def OnBeforeIndex(self):
        self.sql = '''
            select aid,
                   title,
                   intro,
                   mainbody,
                   modify_time,
                   tags,
                   author,
                   author_avatar
              from article_search
        '''
        self.sql_args = None

    def _getRow(self):
        item = self.cur.fetchone()
        if not item:
            return False
        self.aid = int(item[0])
        self.title = item[1]
        self.intro = item[2]
        self.mainbody = item[3]
        self.modify_time = item[4]
        self.tags = item[5]
        self.author = item[6]
        return True


class GroupSource(BaseSource):
    def GetScheme(self):
        return [
            ('gid', {'docid': True}),
            ('name', {'type': 'text'}),
            ('intro', {'type': 'text'}),
            ('motto', {'type': 'text'}),
            ('creater', {'type': 'text'}),
            ('leader', {'type': 'text'}),
        ]

    def GetFieldOrder(self):
        return [
            ('name', 'intro', 'motto', 'creater', 'leader')
        ]

    def OnBeforeIndex(self):
        self.sql = '''
            select gid,
                   name,
                   intro,
                   motto,
                   create_time,
                   tags,
                   creater,
                   leader
              from group_search
        '''
        self.sql_args = None

    def _getRow(self):
        item = self.cur.fetchone()
        if not item:
            return False
        self.gid = int(item[0])
        self.name = item[1]
        self.intro = item[2]
        self.motto = item[3]
        self.create_time = item[4]
        self.tags = item[5]
        self.creater = item[6]
        self.leader = item[7]
        return True


class TopicSource(BaseSource):
    def GetScheme(self):
        return [
            ('tid', {'docid': True}),
            ('title', {'type': 'text'}),
            ('content', {'type': 'text'}),
            ('creater', {'type': 'text'}),
        ]

    def GetFieldOrder(self):
        return [
            ('title', 'content', 'creater')
        ]

    def OnBeforeIndex(self):
        self.sql = '''
            select tid,
                   title,
                   content,
                   create_time,
                   creater
              from topic_search
        '''
        self.sql_args = None

    def _getRow(self):
        item = self.cur.fetchone()
        if not item:
            return False
        self.tid = int(item[0])
        self.title = item[1]
        self.content = item[2]
        self.create_time = item[3]
        self.creater = item[4]
        return True


class UserSource(BaseSource):
    def GetScheme(self):
        return [
            ('uid', {'docid': True}),
            ('nickname', {'type': 'text'}),
            ('intro', {'type': 'text'}),
            ('motto', {'type': 'text'}),
        ]

    def GetFieldOrder(self):
        return [
            ('nickname', 'intro', 'motto')
        ]

    def OnBeforeIndex(self):
        self.sql = '''
            select uid,
                   nickname,
                   avatar,
                   register_time,
                   intro,
                   motto
              from user_search
        '''
        self.sql_args = None

    def _getRow(self):
        item = self.cur.fetchone()
        if not item:
            return False
        self.uid = int(item[0])
        self.nickname = item[1]
        self.avatar = item[2]
        self.register_time = item[3]
        self.intro = item[4]
        self.motto = item[5]
        return True


# 测试: 直接访问演示部分
if __name__ == "__main__":
    conf = {}
    source = ArticleSource(conf)
    source.Connected()
    source.OnBeforeIndex()

    while source.NextDocument():
        pass

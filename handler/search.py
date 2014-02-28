#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.escape import to_unicode, xhtml_escape, to_basestring
from tornado.log import access_log
from lib import sphinxapi, util
from base import BaseHandler, catch_exception
from model import search


class SearchBaseHandler(BaseHandler):
    highlight_opts = {
        'before_match': '<span class="keyword">',
        'after_match': '</span>',
        'force_all_words': True
    }

    @property
    def msearch(self):
        if not hasattr(self, "_search_model"):
            self._search_model = search.SearchModel(self.db)
        return self._search_model

    def render_entry(self, entry):
        keys = ['title', 'nickname', 'intro']
        word_pairs = []

        for word in entry['words'].__reversed__():
            hlword = self.highlight_opts['before_match'] \
                   + word['word']                        \
                   + self.highlight_opts['after_match']
            pair = (to_unicode(word['word']), to_unicode(hlword))
            word_pairs.append(pair)

        for result in entry['results']:
            for key in keys:
                result[key] = xhtml_escape(result[key])

        for word, hlword in word_pairs:
            for result in entry['results']:
                for key in keys:
                    result[key] = result[key].replace(word, hlword)


    def search(self, query, index, page, size, *args, **kwargs):
        offset = (page - 1) * size
        self.client = sphinxapi.SphinxClient()
        self.client.SetConnectTimeout(2000.0)
        self.client.SetLimits(offset, size)
        self.client.SetMatchMode(sphinxapi.SPH_MATCH_EXTENDED2)
        self.client.SetSortMode(sphinxapi.SPH_SORT_RELEVANCE)

        result = self.client.Query(query, index=index)
        if result is None:
            errmsg = self.client.GetLastError()
            access_log.error(errmsg)
            raise Exception(errmsg)

        entry = {
            'query': query,
            'time': result['time'],
            'total_found': result['total_found'],
            'words': result['words'],
            'results': [],
        }

        for match in result['matches']:
            doc_id = match['id']
            item = self.get_item_from_db(doc_id, index)
            entry['results'].append(item)

        self.render_entry(entry)
        return entry

    def get_item_from_db(self, doc_id, doc_type):
        raise NotImplementedError


class SearchHandler(SearchBaseHandler):
    def get_item_from_db(self, doc_id, doc_type):
        if doc_type == 'article':
            article = self.msearch.get_article_item(doc_id)
            item = {
                'url': '/a/' + str(doc_id),
                'title': article['title'],
                'type': 'article',
                'nickname': article['author'],
                'avatar': article['author_avatar'],
                'intro': article['intro'] or '',
                'tags': article['tags'],
                'time': article['modify_time']
            }
        elif doc_type == 'group':
            group = self.msearch.get_group_item(doc_id)
            item = {
                'url': '/g/' + str(doc_id),
                'title': group['name'],
                'type': 'group',
                'nickname': group['creater'],
                'avatar': group['avatar'],
                'intro': group['intro'] or '',
                'tags': group['tags'],
                'time': group['create_time']
            }
        elif doc_type == 'user':
            user = self.msearch.get_user_item(doc_id)
            item = {
                'url': '/user/' + user['nickname'],
                'type': 'user',
                'title': user['nickname'],
                'nickname': user['nickname'],
                'avatar': user['avatar'],
                'intro': user['intro'] or '',
                'time': user['register_time']
            }
        elif doc_type == 'topic':
            topic = self.msearch.get_topic_item(doc_id)
            item = {
                'url': '/t/' + str(doc_id),
                'title': topic['title'],
                'type': 'topic',
                'nickname': topic['creater'],
                'avatar': topic['creater_avatar'],
                'intro': util.get_abstract_str(topic['content'], 100),
                'time': topic['create_time']
            }
        else:
            raise Exception('invalid query type')
        return item

    @catch_exception
    def get(self):
        query = self.get_argument('q', '')
        if not query:
            entry = {
                'query': '',
                'time': 0,
                'total_found': 0,
                'words': [],
                'results': [],
            }
            self.render('search.html', entry=entry)

        index = self.get_argument('type', 'article')
        index = to_unicode(index).encode('utf-8')
        page = int(self.get_argument('page', 1))
        size = int(self.get_argument('size', 10))
        tag = self.get_argument('tag')

        # TODO: 增加对tag的支持
        entry = self.search(query, index, page, size)
        self.render('search.html', entry=entry)


class AutoCompleHandler(SearchBaseHandler):
    pass

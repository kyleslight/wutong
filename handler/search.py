#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.escape import to_unicode, xhtml_escape, to_basestring
from tornado.log import access_log
from lib import sphinxapi
from base import BaseHandler, catch_exception
from model import search
from pprint import pprint


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

        query = '@tags 学科'
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
    """
    /search?type=article&tag=xxx
    /search?q=xxx
    """
    def get_item_from_db(self, doc_id, doc_type):
        article = self.marticle.get_article(doc_id)
        item = {
            'url': '/a/' + str(doc_id),
            'title': article['title'],
            'type': 'article',
            'nickname': article['author'],
            'avatar': article['author_avatar'],
            'intro': article['intro'],
            'tags': article['tags'],
            'time': article['modify_time']
        }
        return item

    @catch_exception
    def get(self):
        query = self.get_argument('q', '')
        index = self.get_argument('type', '*')
        page = int(self.get_argument('page', 1))
        size = int(self.get_argument('size', 10))
        tag = self.get_argument('tag')

        entry = self.search(query, index, page, size)
        self.render('search.html', entry=entry)


class AutoCompleHandler(SearchBaseHandler):
    def do_search(self, query, **kwargs):
        page = int(kwargs['page'])
        size = int(kwargs['size'])
        offset = (page - 1) * size
        search_type = kwargs['search_type']

        if search_type == 'user':
            index = 'opus'
            func = 'get_search_opus'
            sortmode = sphinxapi.SPH_SORT_RELEVANCE
            clause = ''
        elif search_type == 'article_tag':
            sortmode = sphinxapi.SPH_SORT_ATTR_DESC
            clause = 'times'
        elif search_type == 'group_tag':
            sortmode = sphinxapi.SPH_SORT_ATTR_DESC
            clause = 'times'
        else:
            return {'error': 'invalid search type'}

        client = sphinxapi.SphinxClient()
        client.SetMatchMode(sphinxapi.SPH_MATCH_ALL)
        client.SetLimits(offset, size)
        client.SetSortMode(sortmode, caluse)
        result = client.Query(query, index=index)

        if result is None:
            access_log.error(client.GetLastError())
            return {'error': 'search server fault'}

        ids = [d['id'] for d in result['matches']]
        entry = {
            'results': self._get_items_from_db(ids, index),
        }
        return entry

    def get(self):
        query = self.get_argument('q', '')
        search_type = self.get_argument('type', 'user')
        page = self.get_argument('page', 1)
        size = self.get_argument('size', 10)

        entry = self.search(
            query,
            search_type=search_type,
            page=page,
            size=size
        )
        if entry['error']:
            self.write('!: %s' % entry['error'])
        else:
            self.write('search.html', query=query, **entry)

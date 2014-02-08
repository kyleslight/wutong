#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.log import access_log
from lib import sphinxapi
from base import BaseHandler
from pprint import pprint


# TODO: a lot...
class SearchBaseHandler(BaseHandler):
    buildExcerpts_opts = {
        'before_match': '<span class="keyword">',
        'after_match': '</span>',
    }

    def do_search(self, query, **kwargs):
        raise NotImplementedError

    def search(self, query, **kwargs):
        query = query.strip()
        if not query:
            return {'error': 'query not empty'}
        else:
            return self.do_search(query, **kwargs)


class SearchHandler(SearchBaseHandler):
    buildExcerpts_index = 'wutong'

    def _get_items_from_db(self, ids, funcname):
        results = []
        for id in ids:
            item = self.db.calljson(funcname, id)
            results.append(item)
        return results

    def do_search(self, query, **kwargs):
        page = int(kwargs['page'])
        size = int(kwargs['size'])
        offset = (page - 1) * size
        search_type = kwargs['search_type']

        if search_type == 'opus':
            index = 'opus'
            funcname = 'get_search_opus'
        elif search_type == 'group':
            index = 'group'
            funcname = 'get_search_group'
        elif search_type == 'user':
            index = 'user'
            funcname = 'get_search_user'
        else:
            return {'error': 'invalid search type'}

        client = sphinxapi.SphinxClient()
        client.SetMatchMode(sphinxapi.SPH_MATCH_EXTENDED)
        client.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, '@id DESC, @weight DESC')
        client.SetFieldWeights({'title': 10, 'intro': 5})
        client.SetLimits(offset, size)
        result = client.Query(query, index=index)

        if result is None:
            access_log.error(client.GetLastError())
            return {'error': 'search server fault'}

        ids = [d['id'] for d in result['matches']]
        entry = {
            'time': result['time'],
            'total_found': result['total_found'],
            'results': self._get_items_from_db(ids, funcname),
            'error': '',
        }
        pprint(entry)
        # docs = client.BuildExcerpts(
        #     mainbodys,
        #     self.buildExcerpts_index,
        #     query,
        #     self.buildExcerpts_opts
        # )
        return entry

    def get(self):
        query = self.get_argument('q')
        search_type = self.get_argument('type', 'opus')
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
            self.render('search.html', query=query, **entry)


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
        query = self.get_argument('q')
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

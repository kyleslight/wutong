# !/usr/bin/env python
# encoding=utf8
import uuid
import psycopg2
import logging
from psycopg2.extensions import TRANSACTION_STATUS_IDLE
from tornado.escape import json_decode


class Pool(object):
    @classmethod
    def instance(cls, dsn=None, min_size=1, max_size=10000):
        if not hasattr(cls, "_instance"):
            cls._instance = cls(dsn, min_size, max_size)
        return cls._instance

    def __init__(self, dsn, min_size=1, max_size=10000):
        self.pool = []
        self.dsn = dsn
        self.min_size = min_size
        self.max_size = max_size

        assert max_size >= min_size > 0
        for i in xrange(self.min_size):
            self._new_connection()

    def select(self, *arg, **kwargs):
        raise NotImplementedError

    def insert(self, table, d):
        """
        :arg string table:
        :arg dict d:
        """
        sql = 'insert into "%s" ({keys}) values ({values})' % table
        keys = ','.join(['"%s"' % k for k in d.keys()])
        values = ','.join(['%s' for i in xrange(len(d.keys()))])

        sql = sql.format(keys=keys, values=values)
        return self.execute(sql, *d.values())

    def update(self, table, d, where=None, wherevalues=[]):
        """
        :arg string table:
        :arg dict d:
        :arg string where:
        :arg list wherevalues:
        """
        sql = "update %s set ({keys}) = ({values}) {where}" % table
        keys = ','.join(['"%s"' % k for k in d.keys()])
        values = ','.join(['%s' for i in xrange(len(d.keys()))])
        where = 'where ' + where if where else ''

        sql = sql.format(keys=keys, values=values, where=where)
        values = d.values()
        values.extend(wherevalues)
        return self.execute(sql, *values)

    def delete(self, table, where=None, wherevalues=[]):
        """
        :arg string table:
        :arg string where:
        :arg list wherevalues:
        """
        sql = "delete from %s {where}" % table
        where = 'where ' + where if where else ''

        sql = sql.format(where=where)
        return self.execute(sql, *wherevalues)

    def execute(self, sql, *args):
        return self._get_connection().execute(sql, *args)

    def callfirstfield(self, funcname, *args, **kwargs):
        kwargs['function'] = self.getfirstfield
        return self.call(funcname, *args, **kwargs)

    def calljson(self, funcname, *args, **kwargs):
        kwargs['function'] = self.getjson
        return self.call(funcname, *args, **kwargs)

    def callrow(self, funcname, *args, **kwargs):
        kwargs['function'] = self.getrow
        return self.call(funcname, *args, **kwargs)

    def callrows(self, funcname, *args, **kwargs):
        kwargs['function'] = self.getrows
        return self.call(funcname, *args, **kwargs)

    def call(self, funcname, *args, **kwargs):
        sql = 'select %s({placeholder})' % funcname
        placeholder = ','.join(['%s' for i in xrange(len(args))])
        sql = sql.format(placeholder=placeholder)
        func = kwargs.get('function') or self.execute
        return func(sql, *args)

    def getfirstfield(self, sql, *args):
        return self._get_connection().getfirstfield(sql, *args)

    def getjson(self, sql, *args):
        return self._get_connection().getjson(sql, *args)

    def getrow(self, sql, *args):
        return self._get_connection().getrow(sql, *args)

    def getrows(self, sql, *args):
        return self._get_connection().getrows(sql, *args)

    def release(self):
        count_busy = 0
        for cnn in self.pool:
            if cnn.is_busy():
                count_busy += 1

        size = len(self.pool)
        count_free = 0
        if count_busy < self.min_size:
            for cnn in self.pool:
                if not cnn.is_busy():
                    cnn.close()
                    self.pool.remove(cnn)
                    count_free += 1
                if size - count_free == self.min_size:
                    break

    def _new_connection(self):
        cnn = Connection(self.dsn)
        self.pool.append(cnn)
        return cnn

    def _get_connection(self):
        for cnn in self.pool:
            if not cnn.is_busy():
                return cnn
        if len(self.pool) < self.max_size:
            return self._new_connection()


class Connection(object):
    def __init__(self, dsn):
        self.cnn = psycopg2.connect(dsn=dsn)
        self.cur = self.cnn.cursor()

    @property
    def closed(self):
        # 0 = open, 1 = closed, 2 = 'something horrible happened'
        return self.cnn.closed > 0

    def close(self):
        self.cur.close()
        self.cnn.close()

    def is_busy(self):
        return self.cnn.isexecuting() or (self.cnn.closed == 0 and
               self.cnn.get_transaction_status() != TRANSACTION_STATUS_IDLE)

    def mogrify(self, query, *args):
        return self.cur.mogrify(query, args)

    def getrows(self, sql, *args):
        self.execute(sql, *args)
        try:
            result = self.cur.fetchall()
        except:
            result = None
        result = result or [[None]]
        return result

    def getrow(self, sql, *args):
        self.execute(sql, *args)
        try:
            result = self.cur.fetchone()
        except:
            result = None
        result = result or [None]
        return result

    def getfirstfield(self, sql, *args):
        return self.getrow(sql, *args)[0]

    def getjson(self, sql, *args):
        result = self.getfirstfield(sql, *args)
        if isinstance(result, basestring):
            result = json_decode(result)
        if not result:
            result = dict()
        return result

    def execute(self, sql, *args):
        args = args or None
        result = True
        try:
            self.cur.execute(sql, args)
        except Exception as e:
            dbsql = self.mogrify(sql, args)
            logging.error(" `%s` ", dbsql, '\n')
            logging.error(str(e), '\n\n')
            result = False
        self.cnn.commit()
        return result

# encoding=utf8
import uuid
import psycopg2
from psycopg2.extensions import TRANSACTION_STATUS_IDLE
from tornado.escape import json_decode
from util import log

class db_backend:

    @classmethod
    def instance(cls, dsn=None, min_size=1, max_size=10000):
        if not hasattr(cls, "_instance"):
            cls._instance = cls(dsn, min_size, max_size)
        return cls._instance

    def __init__(self, dsn, min_size=1, max_size=10000):
        self.pool = Pool(dsn, min_size, max_size)

    def getfirstfield(self, sql, *args):
        return self.pool.getfirstfield(sql, *args)

    def getitem(self, sql, *args):
        return self.pool.getitem(sql, *args)

    def getitems(self, sql, *args):
        return self.pool.getitems(sql, *args)


    ###########################################################################
    # Do Not Change Argument Position !
    ###########################################################################
    # return str hashuid
    def do_user_register(self, email=None, password=None, penname=None):
        return self.getfirstfield('SELECT f_register_user(%s, %s, %s)',
                                   email, penname, password)

    # return int uid
    def do_activate_user(self, hashuid):
        return self.getfirstfield('SELECT f_activate_user(%s)', hashuid)

    # return int uid
    def do_user_login(self, account=None, password=None):
        return self.getfirstfield('SELECT f_user_login(%s, %s)',
                                   account, password)

    # return dict
    def get_user_info(self, uid):
        return self.getjson('SELECT f_get_user_info_j(%s)', uid)

    # return int
    def get_user_score(self, uid):
        return 0

    # 根据email或penname或phone返回uid
    def get_user_id(self, account=None):
        return self.getfirstfield('SELECT f_get_uid(%s)', account)


    # return int gid
    def create_group(self, name=None, founder=None, intro=None, motton=None):
        return self.getfirstfield('SELECT f_create_group_j(%s, %s, %s, %s)',
                                   name, founder, intro, motton)

    # return bool
    def join_group(self, gid=None, uid=None):
        return self.getfirstfield('SELECT f_join_group(%s, %s)', gid, uid)

    # return dict
    def get_group_info(self, gid):
        return self.getjson('SELECT f_get_group_info_j(%s)', gid)

    # return list<dict>
    # TODO
    def get_group_messages(self, gid, size=30, offset=0):
        results = self.execute('''
                       SELECT * FROM \"group_message\"
                        WHERE gid = %s
                        LIMIT %s
                       OFFSET %s''',
                       gid, size, offset)
        msgs = []
        for res in results:
            msgs.append(dict(
                    gmid=res[0],
                    gid=res[1],
                    uid=res[2],
                    content=res[3],
                    title=res[4],
                    submit_time=res[5],
                    reply_gmid=res[6],
                ))
        return msgs

    def insert_group_chat(self, gid=None, uid=None, content=None, reply_id=None):
        if gid and uid and content:
            return self.execute('''
                         INSERT INTO \"group_chat\"
                                (gid, uid, content, reply_id)
                         VALUES (%s, %s, %s, %s)''',
                        gid, uid, content, reply_id)

class Pool:

    def __init__(self, dsn, min_size=1, max_size=10000):
        self.pool = []
        self.dsn = dsn
        self.min_size = min_size
        self.max_size = max_size

        assert max_size >= min_size > 0
        for i in xrange(self.min_size):
            self._new()

    def getfirstfield(self, sql, *args):
        return self._get_connection().getfirstfield(sql, *args)

    def getitem(self, sql, *args):
        return self._get_connection().getitem(sql, *args)

    def getitems(self, sql, *args):
        return self._get_connection().getitems(sql, *args)

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

    def _new(self):
        cnn = Connection(self.dsn)
        self.pool.append(cnn)
        return cnn

    def _get_connection(self):
        for cnn in self.pool:
            if not cnn.is_busy():
                return cnn
        if len(self.pool) < self.max_size:
            return self._new()


class Connection:
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

    def getitems(self, sql, *args):
        self._execute(sql, *args)
        try:
            result = self.cur.fetchall()
        except:
            result = [[None]]
        return result

    def getitem(self, sql, *args):
        self._execute(sql, *args)
        try:
            result = self.cur.fetchone()
        except:
            result = [None]
        return result

    def getfirstfield(self, sql, *args):
        return self.getitem(sql, *args)[0]

    def getjson(self, sql, *args):
        result = self.getitem(sql, *args)[0]
        if result:
            return json_decode(result)
        else:
            return None

    def _execute(self, sql, *args):
        if not args: args = None
        try:
            self.cur.execute(sql, args)
        except Exception as e:
            dbsql = self.cur.mogrify(sql, args)
            log("ERROR SQL:", dbsql, str(e), separator=False)
        self.cnn.commit()


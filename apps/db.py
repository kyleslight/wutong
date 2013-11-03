# encoding=utf8
import uuid
import psycopg2
from psycopg2.extensions import TRANSACTION_STATUS_IDLE

class db_backend:
    _instance = None

    @classmethod
    def instance(cls, dsn=None, min_size=1, max_size=10000):
        if not cls._instance:
            cls._instance = cls(dsn, min_size, max_size)
        return cls._instance

    def __init__(self, dsn, min_size=1, max_size=10000):
        self.pool = Pool(dsn, min_size, max_size)

    def execute(self, sql, *args):
        return self.pool.execute(sql, *args)

    def do_delete_all_user(self):
        self.execute("DELETE FROM \"user\" * CASCADE")

    def do_delete_all_article(self):
        self.execute("DELETE FROM \"artical\" * CASCADE")

    def do_delete_all_group(self):
        self.execute("DELETE FROM \"group\" * CASCADE")

    def is_user_exists(self, email=None, penname=None):
        if email and penname:
            if not self.execute("""
                        SELECT uid FROM \"user\"
                         WHERE email=%s OR penname=%s""",
                        email, penname):
                return False
        return True

    def do_user_register(self, email=None, password=None, penname=None):
        if email and password and penname:
            # TODO: remove `status`
            return self.execute("""
                        INSERT INTO \"user\"
                               (email,password,penname)
                        VALUES (%s,%s,%s)""",
                        email, password, penname)

    # 邮箱认证通过
    def do_email_check(self, uid):
        if uid:
            if self.execute("""
                    UPDATE \"user\"
                       SET (status)
                         = (%s)
                     WHERE uid = %s""",
                    True, uid):
                return self.execute("""
                            INSERT INTO \"user_info\"
                                   (uid)
                            VALUES (%s)""",
                            uid)

    # return uid
    def do_user_login(self, account=None, password=None):
        if account and password:
            result = self.execute("""
                          SELECT uid FROM \"user\"
                           WHERE status=true
                             AND (email=%s OR penname=%s OR phone=%s)
                             AND password=%s""",
                          account, account, account, password)
            if result:
                return result[0][0]

    def get_user_id(self, account=None):
        if account:
            result = self.execute("""
                          SELECT uid FROM \"user\"
                           WHERE email=%s
                              OR penname=%s
                              OR phone=%s""",
                          account, account, account)
            if result:
                return result[0][0]

    def get_user_info(self, uid):
        result = self.execute("""
                      SELECT * FROM v_user_info
                       WHERE uid = %s""",
                      uid)
        if result:
            result = result[0]
            # TODO
            grade = 0
            # grade = self.execute("""
            #              SELECT *
            #                FROM v_user_grade
            #               WHERE uid = %s""",
            #              uid)[0][0]
            return dict(
                    uid=uid,
                    email=result[0],
                    penname=result[1],
                    phone=result[2],
                    intro=result[3],
                    motton=result[4],
                    avatar=result[5],
                    realname=result[6],
                    sex=result[7],
                    age=result[8],
                    address=result[9],
                    register_date=result[10],
                    warnned_times=result[11],
                    grade=grade,
                )

    # TODO
    def do_join_group(self, uid=None, gid=None):
        if uid and gid:
            return self.execute("""
                        INSERT INTO \"group_user\"
                               (gid,uid)
                        VALUES (%s,%s)""",
                        gid, uid)

    def get_group(self, gid):
        result = self.execute("""
                     SELECT * FROM \"group\"
                      WHERE gid = %s""",
                      gid)
        if result:
            result = result[0]
            return dict(
                    gid=gid,
                    name=result[1],
                    foundTime=result[2],
                    score=result[3],
                    intro=result[4],
                    motton=result[5],
                    founder=result[6],
                    publicity=result[7],
                )

    def get_group_messages(self, gid, size=30, offset=0):
        results = self.execute("""
                       SELECT * FROM \"group_message\"
                        WHERE gid = %s
                        LIMIT %s
                       OFFSET %s""",
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


class Pool:

    def __init__(self, dsn, min_size=1, max_size=10000):
        assert max_size >= min_size > 0
        self.dsn = dsn
        self.min_size = min_size
        self.max_size = max_size
        self._pool = []
        for i in xrange(self.min_size):
            self._new()

    def _new(self):
        cnn = Connection(self.dsn)
        self._pool.append(cnn)
        return cnn

    def _get_connection(self):
        for cnn in self._pool:
            if not cnn.is_busy():
                return cnn
        if len(self._pool) < self.max_size:
            return self._new()

    def _release(self):
        count_busy = 0
        for cnn in self._pool:
            if cnn.is_busy():
                count_busy += 1

        size = len(self._pool)
        count_free = 0
        if count_busy < self.min_size:
            for cnn in self._pool:
                if not cnn.is_busy():
                    cnn.close()
                    self._pool.remove(cnn)
                    count_free += 1
                if size - count_free == self.min_size:
                    break



    def execute(self, sql, *args):
        cnn = self._get_connection()
        return cnn.execute(sql, *args)

class Connection:
    def __init__(self, dsn):
        self.cnn = psycopg2.connect(dsn=dsn)

    def is_busy(self):
        return self.cnn.isexecuting() or (self.cnn.closed == 0 and
               self.cnn.get_transaction_status() != TRANSACTION_STATUS_IDLE)

    def execute(self, sql, *args):
        cur = self.cnn.cursor()
        cur.execute(sql, args)
        self.cnn.commit()
        option = cur.statusmessage.split()[0].upper()
        result = True if option else False
        if option == "SELECT":
            result = cur.fetchall()
        cur.close()
        return result

    @property
    def closed(self):
        # 0 = open, 1 = closed, 2 = 'something horrible happened'
        return self.cnn.closed > 0

    def close(self):
        self.cnn.close()

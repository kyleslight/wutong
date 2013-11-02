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

    def do_delete_all(self):
        self.execute("DELETE FROM \"user\" * CASCADE")
        self.execute("DELETE FROM \"user_info\" * CASCADE")
        self.execute("DELETE FROM \"artical\" * CASCADE")
        self.execute("DELETE FROM \"group\" * CASCADE")

    def is_user_exists(self, email=None, name=None):
        if email and name:
            if not self.execute("""
                        SELECT id FROM \"user\"
                         WHERE email=%s OR name=%s""",
                        email, name):
                return False
        return True

    def do_user_register(self, email=None, password=None, name=None):
        if email and password and name:
            return self.execute("""
                        INSERT INTO \"user\"
                               (email,password,name)
                        VALUES (%s,%s,%s)""",
                        email, password, name)
        return False

    def do_user_login(self, account=None, password=None):
        if account and password:
            result = self.execute("""
                          SELECT id FROM \"user\"
                           WHERE password=%s
                             AND (email=%s OR name=%s)""",
                          password, account, account)
            if result:
                return str(result[0][0])
        return False

    def get_user(self, id):
        result = self.execute("""
                      SELECT * FROM \"user\"
                       WHERE id = %s""",
                      id)
        if result:
            result = result[0]
            result = dict(
                    id=str(result[0]),
                    email=str(result[1]),
                    password=str(result[2]),
                    name=str(result[3]),
                    realname=str(result[4]),
                    register_date=str(result[5]),
                    total_grade=str(result[6]),
                )
        return result

    def do_join_group(self, user_id=None, group_id=None):
        if user_id and group_id:
            return self.execute("""
                        INSERT INTO \"group_user\"
                               (group_id,user_id)
                        VALUES (%s,%s)
                    """,
                    group_id, user_id)
        return False

    def get_user_group(self, user_id):
        self.execute("""
             SELECT id FROM \"group_user\"
              WHERE """)


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

import logging
from tornado.web import RequestHandler
from settings import get_settings
from db import db_backend

class BaseHandler(RequestHandler):
    _db = None

    @property
    def db(self):
        if not self._db:
            dsn = get_settings("dsn")
            self._db = db_backend.instance(dsn)
        return self._db

    def get_user_id(self):
        return self.get_secure_cookie("user_id")

    def get_current_user(self):
        user_id = self.get_user_id()
        if user_id:
            return self.db.get_user(user_id)

    def get(self):
        self.write_error(403)

    def post(self):
        self.write_error(403)

    def echo(self, *msgs):
        if not msgs:
            logging.info('-' * 40)
            return
        cnt = 0
        for msg in msgs:
            cnt += 1
            logging.info(str(cnt) * 40)
            logging.info(msg)

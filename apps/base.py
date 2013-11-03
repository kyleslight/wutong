import logging
from tornado.web import RequestHandler
from settings import settings
from db import db_backend

class BaseHandler(RequestHandler):

    @property
    def db(self):
        return db_backend.instance(settings("dsn"))

    def get_user_id(self):
        return self.get_secure_cookie("user_id")

    def get_current_user(self):
        user_id = self.get_user_id()
        if user_id:
            return self.db.get_user_info(user_id)

    def get(self):
        self.write_error(403)

    def post(self):
        self.write_error(403)

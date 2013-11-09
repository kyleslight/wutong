import logging
from tornado.web import RequestHandler
from settings import settings
from model.db_backend import db_backend

class BaseHandler(RequestHandler):

    @property
    def db(self):
        return db_backend.instance(settings("dsn"))

    def get_user_id(self):
        return self.get_secure_cookie("user_id")

    def get_current_user(self, key=None):
        user_id = self.get_user_id()
        if user_id:
            userinfo = self.db.get_user_info(user_id)
            return userinfo[key] if key else userinfo
        else:
            return GuestUser().__dict__

    def is_guest_user(self, userinfo):
        return userinfo["uid"] == 0

    def get(self):
        self.write_error(403)

    def post(self):
        self.write_error(403)

    def is_null(self):
        self.write_error(403)

class GuestUser():

    def __init__(self):
        self.uid = 0

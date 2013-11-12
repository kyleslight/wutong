from tornado.web import RequestHandler
from model import user, group

class BaseHandler(RequestHandler):

    def get_user_id(self):
        return self.get_secure_cookie("uid")

    def get_current_user(self):
        uid = self.get_user_id()
        user_info = self.usermodel.get_user_info_by_uid(uid)
        return user_info

    def get(self):
        self.write_error(403)

    def post(self):
        self.write_error(403)

    @property
    def db(self):
        return self.application.db

    @property
    def usermodel(self):
        if not hasattr(self, "_usermodel"):
            self._usermodel = user.UserModel(self.db)
        return self._usermodel

    @property
    def groupmodel(self):
        if not hasattr(self, "_groupmodel"):
            self._groupmodel = group.GroupModel(self.db)
        return self._groupmodel

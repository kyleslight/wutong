from tornado.web import RequestHandler
from model import user, group
from lib.session import Session

class BaseHandler(RequestHandler):

    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        self.session = Session(self)

    def on_finish(self):
        self.session.save()

    def is_authenticated(self):
        return self.session.load().get("uid")

    def get_current_user(self):
        user_info = self.usermodel.get_user_info_by_uid(self.user_id)
        return user_info

    @property
    def user_id(self):
        return self.session.get("uid")

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

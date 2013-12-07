import os
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler
from lib.session import Session
from model import user, group
import lib.util

class BaseHandler(RequestHandler):

    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        self.session = Session(self)
        self.db = self.application.db

    def on_finish(self):
        self.session.save()

    def get_current_user(self):
        user_info = self.usermodel.get_user_info(self.user_id)
        return user_info

    @property
    def user_id(self):
        return self.session.get("uid")

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

    def get_module_path(self):
        module_path = os.path.join(self.get_template_path(), "modules")
        return module_path

    def render_module_string(self, module_name, **kwargs):
        module_path = self.get_module_path()
        return self.render_string(os.path.join(module_path, module_name), **kwargs)

import os
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler
from lib.session import Session
from model import user, group, article
import lib.util


class BaseHandler(RequestHandler):
    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        self.session = Session(self)
        self.db = self.application.db
        if not isinstance(self, WebSocketHandler):
            # record last view url
            self.set_cookie('last_view', self.request.uri)

    def on_finish(self):
        self.session.save()

    def get_current_user(self):
        user_info = self.usermodel.get_user_info(self.user_id)
        return user_info

    def get_argument(self, name, default=None):
        return super(BaseHandler, self).get_argument(name, default)

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

    @property
    def articlemodel(self):
        if not hasattr(self, "_articlemodel"):
            self._articlemodel = article.ArticleModel(self.db)
        return self._articlemodel

    def get_module_path(self):
        module_path = os.path.join(self.get_template_path(), "modules")
        return module_path

    def render_module_string(self, module_name, **kwargs):
        module_path = self.get_module_path()
        return self.render_string(os.path.join(module_path, module_name), **kwargs)

    def get(self):
        self.write_error(404)

    def post(self):
        self.write_error(403)

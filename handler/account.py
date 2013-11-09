from tornado import escape
from tornado.web import authenticated
from base import BaseHandler
from util import createpasswd, log

class AccountHandler(BaseHandler):
    def register(email=None, password=None, name=None):
        result = self.db.do_user_register(email=email, password=password, name=username)
        return result


    def login(account=None, password=None):
        password = createpasswd(password)
        user_id = self.db.do_user_login(account=account, password=password)
        if user_id:
            self.set_secure_cookie("user_id", user_id, 5, httponly=True)
        return user_id

class LoginHandler(BaseHandler):
    def get(self):
        self.write("")

    def post(self):
        username = self.get_argument("username", None)
        password = self.get_argument("password", None)

        if self.login(username, password):
            self.write("success")
        else:
            self.write("failed")


class LogoutHandler(BaseHandler):

    def post(self):
        self.clear_cookie("user_id")

class RegisterHandler(BaseHandler):

    def post(self):
        username = self.get_argument("username", None)
        password = self.get_argument("password", None)
        email = self.get_argument("email", None)

        if username and password and email:
            password = createpasswd(password)
            if self.login(username, password):
                self.write("success")
                return
        self.write("failed")

class UserinfoHandler(BaseHandler):

    @authenticated
    def get(self):
        userinfo = self.get_current_user()
        userinfo["register_date"] = str(userinfo["register_date"])
        userinfo = escape.json_encode(userinfo)
        self.write(userinfo)

class CheckHandler(BaseHandler):
    def check_mail(hashstr):
        pass

    def post(self):
        hashstr = self.get_argument("r", None)
        self.check_mail(hashstr)

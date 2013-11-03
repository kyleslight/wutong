from tornado import escape
from tornado.web import authenticated
from base import BaseHandler
from util import createpasswd, echo

class LoginHandler(BaseHandler):
    def get(self):
        self.write("")

    def post(self):
        username = self.get_argument("username", None)
        password = self.get_argument("password", None)
        if username and password:
            password = createpasswd(password)
            user_id = self.db.do_user_login(account=username, password=password);
            if user_id:
                user_id = str(user_id)
                self.set_secure_cookie("user_id", user_id, 5, httponly=True)
                self.write("success")
                return
        self.write("failed")


class LogoutHandler(BaseHandler):

    def post(self):
        self.clear_cookie("user_id")

class RegisterHandler(BaseHandler):

    def post(self):
        username = self.get_argument("username", None)
        password = self.get_argument("password", None)
        email = self.get_argument("email", None)
        self.echo(username, password, email)
        if username and password and email:
            if self.db.is_user_exists(email=email, name=username):
                self.write("user_exists")
                return
            password = createpasswd(password)
            if self.db.do_user_register(email=email, password=password,
                                        name=username):
                user_id = self.db.do_user_login(account=email, password=password)

                self.set_secure_cookie("user_id", user_id, 5, httponly=True)
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


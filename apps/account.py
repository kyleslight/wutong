from base import BaseHandler
from util import createpasswd

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
                self.set_secure_cookie("user_id", user_id, 5, httponly=True)
                self.write("success")
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



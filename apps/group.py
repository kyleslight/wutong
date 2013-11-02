from base import BaseHandler

class IndexHandler(BaseHandler):

    def get(self):
        self.render("group.html")

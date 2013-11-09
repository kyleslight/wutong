from datetime import datetime
from tornado.web import authenticated
from tornado.websocket import WebSocketHandler
from tornado.escape import json_encode, json_decode
from base import BaseHandler
from lib.util import log

class IndexHandler(BaseHandler):

    def get(self, id=None):
        # message[] = to_basestring(self.render_string("message.html", messages=messages))
        self.render("group.html", messages=[])

    @authenticated
    def post(self, id):
        pass

class MessageHandler(BaseHandler, WebSocketHandler):
    members = dict()

    def is_member(self, uid):
        return True

    def open(self, gid):
        self.gid = gid
        if not self.members.get(gid, None):
            self.members[gid] = list()

        self.members[gid].append(self)
        self.user = self.get_current_user()

    def on_close(self):
        self.members[self.gid].remove(self)

    def on_message(self, json_data):
        uid=self.user["uid"]
        if json_data and self.is_member(uid):
            data = json_decode(json_data)
            content = data["content"]
            title = data["title"]

            if title:
                self.db.insert_group_topic(self.gid, uid, content, title)
            else:
                self.db.insert_group_chat(self.gid, uid, content)

            entry = dict(
                    penname=self.user["penname"],
                    content=content,
                    submit_time=str(datetime.now()),
                    avatar=self.user["avatar"],
                    title=title,
                )
            log(entry)
            for self.mem in self.members[self.gid]:
                self.mem.write_message(json_encode(entry))



#!/usr/bin/env python
# -*- coding: utf-8 -*-

class GroupModel:

    def __init__(self, db):
        self.db = db

    def do_create(self, name, founder, intro, motton):
        select = 'SELECT f_create_group_j(%s, %s, %s, %s)'
        gid = self.getfirstfield(select, name, founder, intro, motton)
        return gid

    def do_user_join_group(self, uid, gid):
        select = 'SELECT f_join_group(%s, %s)'
        trueorfalse = self.getfirstfield(select, gid, uid)
        return trueorfalse

    def get_group_info(self, gid):
        select = 'SELECT f_get_group_info_j(%s)'
        group_info = self.getjson(select, gid)
        return group_info

    # return list<dict>
    # TODO
    def get_group_messages(self, gid, size=30, offset=0):
        results = self.execute('''
                       SELECT * FROM \"group_message\"
                        WHERE gid = %s
                        LIMIT %s
                       OFFSET %s''',
                       gid, size, offset)
        msgs = []
        for res in results:
            msgs.append(dict(
                    gmid=res[0],
                    gid=res[1],
                    uid=res[2],
                    content=res[3],
                    title=res[4],
                    submit_time=res[5],
                    reply_gmid=res[6],
                ))
        return msgs

    def insert_group_chat(self, gid, uid, content, reply_id):
        if gid and uid and content:
            return self.execute('''
                         INSERT INTO \"group_chat\"
                                (gid, uid, content, reply_id)
                         VALUES (%s, %s, %s, %s)''',
                        gid, uid, content, reply_id)

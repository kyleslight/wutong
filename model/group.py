#!/usr/bin/env python
# -*- coding: utf-8 -*-

class GroupModel:

    def __init__(self, db):
        self.db = db

    def do_create(self, name, founder, intro, motton):
        select = 'SELECT f_create_group(%s, %s, %s, %s)'
        gid = self.db.getfirstfield(select, name, founder, intro, motton)
        return gid

    def do_user_join_group(self, gid, uid):
        select = 'SELECT f_join_group(%s, %s)'
        return self.db.execute(select, gid, uid)

    def do_insert_message(self, gid, uid, content, title=None, reply_id=None):
        select = 'SELECT f_insert_group_message(%s, %s, %s, %s, %s)'
        return self.db.getfirstfield(select, gid, uid, content, title, reply_id)

    def get_group_info(self, gid):
        select = 'SELECT f_get_group_info_j(%s)'
        group_info = self.db.getjson(select, gid)
        return group_info

    def get_group_message(self, message_id):
        select = 'SELECT f_get_group_message_j(%s)'
        message = self.db.getjson(select, message_id)
        return message

    def get_group_messages(self, gid, size, offset):
        select = 'SELECT f_get_group_messages_j(%s, %s, %s)'
        messages = self.db.getjson(select, gid, size, offset)
        return messages

    def get_member_info(self, gid, uid):
        select = 'SELECT f_get_member_info_j(%s, %s)'
        return self.db.getjson(select, gid, uid)

    def get_group_bulletins(self, gid, size, offset):
        select = 'SELECT f_group_bulletins_j(%s, %s, %s)'
        bulletins = self.db.getjson(select, gid, size, offset)
        return bulletins

    def do_insert_bulletin(self, gid, uid, content, title):
        select = 'SELECT f_insert_group_bulletin(%s, %s, %s, %s)'
        return self.db.getfirstfield(select, gid, uid, content, title)

    def update_group_info(self, gid, founder, name, intro, motton):
        select = 'SELECT f_update_group_info(%s, %s, %s, %s, %s)'
        return self.db.execute(select, gid, founder, name, intro, motton)

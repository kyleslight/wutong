#!/usr/bin/env python
# -*- coding: utf-8 -*-


class NotificationModel(object):
    def __init__(self, db):
        self.db = db

    def _get_notifications(self, uid, limit=5, offset=0, type=None):
        select = '''select *
                      from notification
                     where uid = %s
                       and type = %s
                     limit = %s
                    offset = %s'''
        notifications = self.db.getjson(select, uid, type, limit, offset)
        return notifications

    def _create_notification(self,
                             uid,
                             penname,
                             title,
                             content,
                             notication_type):
        select = 'SELECT create_notification(%s, %s, %s, %s, %s)'
        notification_id = self.db.getfirstfield(
            select,
            uid,
            penname,
            title,
            content,
            notication_type
        )
        return notification_id

    def create_reply(self, uid, penname, title, content):
        return self._create_notification(uid, penname, title, content, '回复')

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Last Modified time: 2013-12-06 23:16:55

import os
import uuid
from hashlib import sha1
from datetime import datetime
from tornado.web import create_signed_value, decode_signed_value


def hexstring(salt, string):
    hexstr = sha1((salt + string).encode("utf-8"))
    hexstr = sha1(hexstr.hexdigest().encode("utf-8"))
    hexstr = str(hexstr.hexdigest())
    return hexstr

encrypt_url = None
def _secret_and_name():
    url = encrypt_url or "secret.wutong.com"
    secret = uuid.uuid5(uuid.NAMESPACE_URL, url).hex
    name = uuid.uuid3(uuid.NAMESPACE_URL, url).hex
    return secret, name

def encodestr(s):
    secret, name = _secret_and_name()
    return create_signed_value(secret, name, s)

def decodestr(encrpstr):
    secret, name = _secret_and_name()
    return decode_signed_value(secret, name, encrpstr)

def str2datetime(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")

def prettytime(dt):
    if isinstance(dt, basestring):
        dt = str2datetime(dt)
    dtdate = dt.date()
    now = datetime.now()
    nowdate = now.date()

    if nowdate == dtdate:
         return dt.strftime("%H:%M:%S")
    else:
         return dt.strftime("%Y-%m-%d %H:%M")

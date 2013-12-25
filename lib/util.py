#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Last Modified time: 2013-12-25 03:07:59

import os
import uuid
import Image
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

def filesuffix(filename):
    return filename.rsplit('.', 1)[-1]

def addsuffix(basename, suffix):
    return basename + '.' + suffix

def genavatar(avatar_fp, avatar_dir, avatar_name):
    avatar = Image.open(avatar_fp)
    # crop avatar if it's not square
    avatar_w, avatar_h = avatar.size
    avatar_border = avatar_w if avatar_w < avatar_h else avatar_h
    avatar_crop_region = (0, 0, avatar_border, avatar_border)
    avatar = avatar.crop(avatar_crop_region)

    avatar_100x100 = avatar.resize((100, 100), Image.ANTIALIAS)
    avatar_50x50 = avatar.resize((50, 50), Image.ANTIALIAS)
    avatar_32x32 = avatar.resize((32, 32), Image.ANTIALIAS)

    avatar_name = os.path.join(avatar_dir, avatar_name)
    avatar_normal = "%s_normal.png" % avatar_name
    avatar_100x100.save(avatar_normal, "PNG")
    avatar_50x50.save("%s_thumb.png" % avatar_name, "PNG")
    avatar_32x32.save("%s_mini.png" % avatar_name, "PNG")
    return os.path.basename(avatar_normal)


def avatarurl(url, size='normal'):
    if url.startswith('http://') or url.startswith('https://'):
        return url
    else:
        return os.path.join('/static/avatar', url)

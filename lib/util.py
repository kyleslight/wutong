#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Last Modified time: 2014-02-14 15:06:58

import os
import re
import uuid
import time
import string
import random
try:
    from PIL import Image
except ImportError:
    import Image
from hashlib import sha1
from datetime import datetime
from Crypto.Cipher import AES
from Crypto import Random
from tornado.web import create_signed_value, decode_signed_value


illegal_chars = set("""`~!@#$%^&*()+<>?:;'"[]{},./\\| \t\n\r""")
def has_illegal_char(s):
    if set(s).intersection(illegal_chars):
        return True
    return False

def is_bool(s):
    return s.lower() in ('0', '1', 't', 'f', 'true', 'false')

def get_bool(s):
    s = s.lower()
    if s in ('1', 't', 'true'):
        return True
    elif s in ('0', 'f', 'false'):
        return False
    return None

def is_english_or_chinese(s):
    if all(u'\u4e00' <= c <= u'\u9fff' for c in s):
        return True
    elif all(c.isspace() or c.isalpha() for c in s):
        return True
    return False

def is_email(email):
    pattern = re.compile(r'^[\.\w]{1,}[@]\w+[.]\w+$')
    if pattern.match(email):
        return True
    return False

def is_phone(phone):
    pattern = re.compile(r'^13\d{1}\d{8}$|15[0189]{1}\d{8}$|189\d{8}$')
    if pattern.match(phone):
        return True
    return False

def is_time(time):
    return True if str2time(time) else False

def get_abstract_str(s, length=10, suffix=u'...'):
    title = s[:10]
    if len(s) > 10:
        title += suffix
    return title

def str2time(s):
    """
    convert `str` to `struct_time`
    """
    t = None
    try:
        t = time.strptime(s, "%Y-%m-%d")
    except ValueError:
        try:
            t = time.strptime(s, "%Y-%m-%d %H:%M:%S")
        except:
            pass
    return t

def split(txt, seps=u';；'):
    default_sep = seps[0]
    for sep in seps[1:]:
        txt = txt.replace(sep, default_sep)
    return [i.strip() for i in txt.split(default_sep)]

def random_string(size, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

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

def encrypt(s):
    key = bytes(random_string(16))
    iv = random_string(8).encode("hex")
    cipher = AES.new(key, AES.MODE_CFB, iv)
    encrys = (key + cipher.encrypt(bytes(s)) + iv).encode("hex")
    return encrys

def decrypt(s):
    s = s.decode("hex")
    key = s[:16]
    iv = s[-16:]
    s = s[16:-16]
    cipher = AES.new(key, AES.MODE_CFB, iv)
    return cipher.decrypt(s)

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
    if url is None:
        url = 'unknow_normal.png'
    if url.startswith('http://') or url.startswith('https://'):
        return url
    else:
        return os.path.join('/static/avatar', url)

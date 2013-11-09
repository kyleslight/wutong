import logging
from hashlib import sha1
from uuid import uuid3, NAMESPACE_X500

def hexstring(salt, string):
    hexstr = sha1((salt + string).encode("utf-8"))
    hexstr = sha1(hexstr.hexdigest().encode("utf-8"))
    hexstr = str(hexstr.hexdigest())
    return hexstr

def createpasswd(value):
    value = str(value).encode("utf-8")
    salt = str(uuid3(NAMESPACE_X500, value).hex)
    enpasswd = hexstring(salt, value)
    enpasswd += salt
    while len(enpasswd) < 128:
        enpasswd += str(sha1(enpasswd).hexdigest())
    enpasswd = enpasswd[:128]
    return enpasswd

def log(*objs, **kwargs):
    sepsort = kwargs.get("sep", '-')
    seplen = kwargs.get("length", 40)

    if sepsort == "number":
        sep = '0'
    else:
        sep = sepsort
    if not objs:
        logging.info(sep * seplen)
        return

    cnt = 0
    for obj in objs:
        cnt += 1

        if sepsort == "number":
            sep = str(cnt)
        logging.info(sep * seplen)
        if hasattr(obj, "__name__"):
            msg = obj.__name__
        else:
            msg = str(obj)
        logging.info(msg)

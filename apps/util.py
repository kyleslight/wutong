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

def echo(*msgs):
    seplen = 40

    if not msgs:
        logging.info('-' * seplen)
        return
    cnt = 0
    for msg in msgs:
        cnt += 1
        logging.info(str(cnt) * seplen)
        logging.info(msg)

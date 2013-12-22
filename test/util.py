#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import requests
import random
_path = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(_path)
from model.db import Pool
from model.user import UserModel
from model.group import GroupModel
from model.article import ArticleModel
import q


dsn_test = "host=%s dbname=%s user=%s password=%s" % (
    "localhost", "wutong_test", "wutong", "wutong"
)

db_test = Pool.instance(dsn_test)

def path(p):
    # return abspath(wutong)/p
    return os.path.join(_path, p)

def gen_random_user(num=1):
    """
    Generate random user from randomuser.me
    """
    users = []
    results = []

    for i in xrange(num / 5):
        response = requests.get('http://api.randomuser.me/?results=5')
        results += response.json()['results']
    response = requests.get('http://api.randomuser.me/?results=' + str(num % 5))
    results += response.json()['results'] or []

    for res in results:
        user = res["user"]
        user["penname"] = user["name"]["first"] + user["name"]["last"]
        user["password"] = 'wutong'
        user["sex"] = user["gender"]
        user["address"] = user["location"]["city"] + user["location"]["state"]
        user["avatar"] = user["picture"]
        user["intro"] = user["sha1_hash"]
        user["motton"] = user["md5_hash"]
        user["age"] = user["location"]["zip"][-2:]
        users.append(user)

    return users

def gen_test_data(number=30):
    admin = {
        'email': 'test@wutong.com',
        'penname': 'wutong',
        'password': 'wutong',
    }
    sqlpath = path("model/dbschema/") + "schema.sql"

    sql = open(sqlpath, "r").read()
    assert(db_test.execute(sql))
    usermodel = UserModel(db_test)
    groupmodel = GroupModel(db_test)
    articlemodel = ArticleModel(db_test)

    hashuid = usermodel.do_register(admin['email'],
                                    admin['penname'],
                                    admin['password'])
    admin["uid"] = usermodel.do_activate(hashuid)

    users = gen_random_user(number)
    # user
    for user in users:
        hashuid = usermodel.do_register(user["email"],
                                        user["penname"],
                                        user["password"])
        user["uid"] = usermodel.do_activate(hashuid)
        usermodel.update_user_info(**user)

    gid = groupmodel.do_create(user['uid'], 'test_group1')
    gid2 = groupmodel.do_create(admin['uid'], 'test_group2', is_public=False)
    tids = []
    # group
    for user in users:
        uid = user['uid']
        groupmodel.do_join_group(gid, uid)
        groupmodel.do_join_group(gid2, uid)
        tid = groupmodel.do_create_topic(gid, uid, 'topic', '%s content' % gid)
        tids.append(tid)
        groupmodel.do_create_chat(gid, uid, '%s chat' % gid)
        groupmodel.do_create_bulletin(gid, uid, 'title', '%s bulletin' % gid)

    # topic and chat
    for i in xrange(number * 10):
        uid = random.choice(users)['uid']
        tid = random.choice(tids)
        if bool(random.getrandbits(1)):
            groupmodel.do_create_chat(gid, uid, 'topic chat', tid)
        else:
            tid = groupmodel.do_create_topic(gid,
                                             uid,
                                             'child%s topic' % random.random(),
                                             'content%s' % random.random(),
                                             tid)
            tids.append(tid)

    # article
    aids = []
    for i in xrange(number * 3):
        uid = random.choice(users)['uid']
        aid = articlemodel.do_create(uid,
                                     'title%s' % random.random(),
                                     'mainbody')
        aids.append(aid)
        for i in xrange(random.randint(0, number * 30)):
            uid = random.choice(users)['uid']
            articlemodel.create_bottom_comment(aid,
                                               uid,
                                               'content%s' % random.random())
            articlemodel.create_side_comment(aid,
                                             uid,
                                             'content%s' % random.random(),
                                             str(random.randint(0,1)))


if __name__ == "__main__":
    try:
        number = int(sys.argv[1])
    except IndexError:
        number = 30
    gen_test_data(number)

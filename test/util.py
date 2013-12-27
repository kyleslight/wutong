#!/usr/bin/env python
# -*- coding: utf-8 -*-

import __builtin__
import sys
import os
import requests
import random
_path = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(_path)
from lib.util import genavatar
from model.db import Pool
from model.user import UserModel
from model.group import GroupModel
from model.article import ArticleModel
import q
__builtin__.__dict__['q'] = q


dsn_test = "host=%s dbname=%s user=%s password=%s" % (
    "localhost", "wutong_test", "wutong", "wutong"
)
db_test = Pool.instance(dsn_test)


def wutong_path(p):
    # return abspath(wutong)/p
    return os.path.join(_path, p)

def random_bool():
    return bool(random.getrandbits(1))

class TestDataGenerator(object):
    def __init__(self, number):
        self.number = number
        self.db = db_test
        self.user = UserModel(self.db)
        self.group = GroupModel(self.db)
        self.article = ArticleModel(self.db)
        self.admin = {
            'email': 'test@wutong.com',
            'penname': 'wutong',
            'password': 'wutong',
        }

        self.gen_test_data()

    def gen_database_table(self):
        sqlpath = wutong_path("model/dbschema/") + "schema.sql"
        sql = open(sqlpath, "r").read()
        assert(self.db.execute(sql))

    def gen_admin_user(self):
        hashuid = self.user.do_register(self.admin['email'],
                                        self.admin['penname'],
                                        self.admin['password'])
        self.admin["uid"] = self.user.do_activate(hashuid)

        # gen avatar
        avatar_dir = os.path.join(os.path.dirname(__file__),
                                  '../static/avatar/')
        random_path = os.path.join(avatar_dir, 'random')
        avatar_path = os.path.join(random_path,
                                   random.choice(os.listdir(random_path)))

        with open(avatar_path, 'r') as avatar_fp:
            avatar = genavatar(avatar_fp, avatar_dir, self.admin['penname'])
            self.user.update_user_avatar_by_penname(
                self.admin['penname'],
                avatar
            )

        return self.admin

    def gen_users(self):
        """
        Generate random user from randomuser.me
        """
        url = 'http://api.randomuser.me/?results=%s'
        users = []
        results = []

        for i in xrange(self.number / 5):
            response = requests.get(url % 5)
            results += response.json()['results']
        response = requests.get(url % (self.number % 5))
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

        # insert into db
        for user in users:
            hashuid = self.user.do_register(user["email"],
                                            user["penname"],
                                            user["password"])
            user["uid"] = self.user.do_activate(hashuid)
            self.user.update_user_avatar_by_penname(
                user['penname'],
                user['avatar']
            )

        return users

    def gen_groups(self, users):
        gid = self.group.do_create(self.admin['uid'], 'admin_group')
        gids = [gid]
        for i in xrange(random.randint(1, self.number)):
            user = random.choice(users)
            gid = self.group.do_create(
                user['uid'],
                '%s group by %s' % (random.random(), user['uid']),
                is_public=random_bool()
            )
            self.group.do_join_group(gid, self.admin["uid"])
            gids.append(gid)

        return gids

    def gen_random_group_data(self, users, gids):
        tids = []
        cids = []
        bids = []

        def random_reply_id():
            if random_bool():
                try:
                    return random.choice(tids)
                except:
                    pass
            return None

        for gid in gids:
            uid = random.choice(users)['uid']
            self.group.do_join_group(gid, uid)

            tid = self.group.do_create_topic(
                gid,
                uid,
                'random topic in group %s by %s' % (gid, uid),
                '%s' % random.random(),
                random_reply_id()
            )
            tids.append(tid)

            cid = self.group.do_create_chat(
                gid,
                uid,
                'random chat in group %s' % gid,
                random_reply_id()
            )
            cids.append(cid)

            bid = self.group.do_create_bulletin(
                gid,
                uid,
                'random bulletin in group %s' % gid,
                '%s' % random.random()
            )
            bids.append(bid)

        return tids, cids, bids

    def gen_articles(self, users):
        aids = []

        for i in xrange(random.randint(self.number, self.number * 10)):
            uid = random.choice(users)['uid']
            aid = self.article.do_create(
                uid,
                '%s article title by %s' % (random.random(), uid),
                '<p>random mainbody %s</p>' % random.random(),
                tags=['技术', 'linux', 'python']
            )
            aids.append(aid)

        return aids

    def gen_random_article_data(self, users, aids):
        for aid in aids:
            for i in xrange(random.randint(0, self.number)):
                uid = random.choice(users)['uid']
                self.article.create_bottom_comment(
                    aid,
                    uid,
                    '%s comment' % random.random()
                )
                paragraph_id = str(random.randint(0,1))
                self.article.create_side_comment(
                    aid,
                    uid,
                    '%s comment' % random.random(),
                    paragraph_id
                )

    def gen_test_data(self):
        self.gen_database_table()
        admin = self.gen_admin_user()
        users = self.gen_users()
        gids = self.gen_groups(users)
        tids, cids, bids = self.gen_random_group_data(users, gids)
        aids = self.gen_articles(users)
        self.gen_random_article_data(users, aids)


if __name__ == "__main__":
    try:
        number = int(sys.argv[1])
    except IndexError:
        number = 3
    TestDataGenerator(number)

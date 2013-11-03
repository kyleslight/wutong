# encoding=utf8
from settings import settings
from apps.db import db_backend
from apps.util import *
from main import main

if __name__ == "__main__":
    db = db_backend.instance(settings("dsn"))
    # 重新创建表
    db.execute(open("schema.sql", "r").read())
    # db.do_delete_all_user()
    # db.do_delete_all_group()
    # db.do_delete_all_article()

    email = "lfz@sicun.org"
    password = "test"
    penname = "test"

    db.do_user_register(email=email,
                        password=createpasswd(password),
                        penname=penname)
    uid = db.get_user_id(email)
    db.do_email_check(uid)
    uid = db.do_user_login(account=penname,
                           password=createpasswd(password))
    echo(uid, db.get_user_info(uid))
    main()

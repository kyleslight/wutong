from settings import settings
from apps.db import db_backend
from apps.util import *
from main import main

if __name__ == "__main__":
    db = db_backend.instance(settings("dsn"))
    db.execute(open("schema.sql", "r").read())
    db.do_delete_all()

    db.do_user_register(email="lfz@sicun.org", password=createpasswd(1), name="register")
    user_id = db.do_user_login(account="lfz@sicun.org", password=createpasswd(1))
    echo(user_id)
    echo(db.get_user(user_id))
    main()

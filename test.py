from settings import get_settings
from apps.db import db_backend
from apps.util import createpasswd
import logging

if __name__ == "__main__":
    settings = get_settings()
    db = db_backend.instance(settings["dsn"])

    db.do_delete_all()
    db.do_user_register(email="lfz@sicun.org", password=createpasswd(1), name="register")
    user = db.do_user_login(email="lfz@sicun.org", password=createpasswd(1))
    logging.info(user)

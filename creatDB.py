#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""SchoolCMS.

CreatDB.

DB ver -100

"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from .util.parse_config import parse_config
parse_config()

from . import version as system_version
from .db import engine, Base, SessionGen
from .db import System, FileList
from .db import version as db_version

from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm.exc import NoResultFound


def creat_db(sql_session):
    Base.metadata.create_all(engine)

    session.add_all([
            System('system_version', system_version),
            System('db_version', db_version)
        ])
    session.commit()
    print('資料庫初始化程序完成')


if __name__ == '__main__':
    with SessionGen() as session:
        try:
            info = System.by_key('system_version', session).one()
        except (ProgrammingError, NoResultFound) as e:
            try:
                creat_db(session)
            except KeyboardInterrupt:
                print('\n初始化程序取消')
        else:
            print('資料庫已經初始化，初始化程序停止。如果想要重新初始化，請先清空資料庫。')

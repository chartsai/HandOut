#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""HandOut db model filelist.

File list.
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from . import Base

import re
import mimetypes
from datetime import datetime

from sqlalchemy import Column, func
from sqlalchemy.dialects.mysql import INTEGER, CHAR, VARCHAR, TEXT, TIMESTAMP


class FileList(Base):
    __tablename__ = 'filelist'

    key = Column(CHAR(40, collation='utf8_unicode_ci'), primary_key=True)
    filename = Column(TEXT(charset='utf8'), nullable=False)
    file_type = Column(CHAR(10, collation='utf8_unicode_ci'))
    present_id = Column(INTEGER, nullable=False)
    created = Column(TIMESTAMP, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        self.key = kwargs['key']
        self.filename = kwargs['filename']
        self.file_type = kwargs['file_type']
        self.present_id = kwargs['present_id']

    def __repr__(self):
        return 'FileList(%s ,%s)' % \
        (self.key,self.filename)

    @classmethod
    def by_key(cls, key, sql_session):
        q = sql_session.query(cls)
        return q.filter(cls.key == key)

    @classmethod
    def by_present_id(cls, present_id, sql_session):
        q = sql_session.query(cls)
        return q.filter(cls.present_id == present_id)

    def to_dict(self):
        return {
            'key' : self.key,
            'filename' : self.filename,
            # 'filetype' : 'file',
        }

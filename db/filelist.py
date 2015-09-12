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
    content_type = Column(TEXT(charset='utf8'), nullable=False)
    present_key = Column(CHAR(40, collation='utf8_unicode_ci'), nullable=False)
    created = Column(TIMESTAMP, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        self.key = kwargs['key']
        self.filename = kwargs['filename']
        self.content_type = kwargs['content_type']
        self.present_key = kwargs['present_key']

    def __repr__(self):
        return 'FileList(%s ,%s)' % \
        (self.key,self.filename)

    @classmethod
    def by_key(cls, key, sql_session):
        q = sql_session.query(cls)
        return q.filter(cls.key == key)

    @classmethod
    def by_present_key(cls, present_key, sql_session):
        q = sql_session.query(cls)
        return q.filter(cls.present_key == present_key)

    def to_dict(self):
        return {
            'key' : self.key,
            'filename' : self.filename,
            # 'filetype' : 'file',
        }

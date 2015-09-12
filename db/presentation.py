#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""HandOut db model Presentation.

A model.
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from . import Base

from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import INTEGER, DOUBLE, VARCHAR, TEXT, TIMESTAMP


class Presentation(Base):
    __tablename__ = 'presentations'

    p_key = Column(INTEGER, primary_key=True)
    title = Column(VARCHAR(40, collation='utf8_unicode_ci'), nullable=False)
    owner = Column(VARCHAR(40, collation='utf8_unicode_ci'), nullable=False)
    lat = Column(DOUBLE, nullable=False)
    lng = Column(DOUBLE, nullable=False)
    created = Column(TIMESTAMP, default=datetime.utcnow)
    updated = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        self.title = kwargs['title']
        self.owner = kwargs['owner']
        self.lat = kwargs['lat']
        self.lng = kwargs['lng']

    @classmethod
    def by_p_key(cls, p_key, sql_session):
        q = sql_session.query(cls)
        q = q.filter(cls.p_key == p_key)
        return q

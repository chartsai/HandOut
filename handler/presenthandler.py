#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""HandOut presentation."""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from . import BaseHandler
from ..db import Presentation, FileList

import re
import os
import uuid
import shutil
import subprocess
import math
from decimal import Decimal
# import mimetypes
# from datetime import datetime

try:
    xrange
except NameError:
    xrange = range


def _get_float(s, default):
    try:
        f = float(s)
    except ValueError:
        return default
    return f

EARTH_R = Decimal('6371009') # Meter
RAD_K = Decimal.from_float(math.pi) / Decimal(180)

class QueryPresentHandler(BaseHandler):
    def get(self):
        # TODO: Get data
        self.lat = RAD_K*Decimal.from_float(_get_float('25.0724763', Decimal(0)))
        self.lng = RAD_K*Decimal.from_float(_get_float('121.5185635', Decimal(0)))

        # TODO: Query out less point
        presents = self.sql_session.query(Presentation).all()
        for i in xrange(len(presents)):
            lat2 = RAD_K*presents[i].lat
            lng2 = RAD_K*presents[i].lng
            presents[i].distance_string = self._distance_string(lat2, lng2)
        self.render('querypresent.html', presents = presents)

    def _distance_string(self, lat2, lng2):
        a = abs(self.lat - lat2)
        b = abs(self.lng - lng2)
        s = 2*math.asin(math.sqrt(math.pow(math.sin(a/2),2)+math.cos(self.lat)*math.cos(lat2)*math.pow(math.sin(b/2),2)))
        d = EARTH_R*Decimal.from_float(s)
        d_i = d.to_integral()
        if d_i < 1000:
            return ('%d m' % d_i)
        else :
            return ('%.2f km' % (float(d_i/1000)))


class ViewPresentHandler(BaseHandler):
    def get(self, present_id):
        present = Presentation.by_p_key(present_id, self.sql_session).scalar()
        present_file = FileList.by_present_id(present_id, self.sql_session).scalar()
        self.render('viewpresent.html',
                        title = present.title,
                        owner = present.owner,
                        file_path = '/download/%s/%s' % (present_file.key, present_file.filename))


_file_type_re = re.compile(r'^(.*)[.](.*)$')

class SubmitPresentHandler(BaseHandler):
    def initialize(self):
        super(SubmitPresentHandler, self).initialize()
        self.file_folder = os.path.join(os.path.dirname(__file__), '../file')
        if not os.path.exists(self.file_folder):
            os.makedirs(self.file_folder)

    def prepare(self):
        super(SubmitPresentHandler, self).prepare()
        self.kw = {
            'present_id': '',
            'title': '',
            'owner': '',
            'lat': 0.0,
            'lng': 0.0,
            'presentation': {},
        }

    def get(self, present_id):
        if present_id:
            old_present = Presentation.by_p_key(present_id, self.sql_session).scalar()
            if not old_present:
                raise self.HTTPError(404)
            self.kw['present_id'] = present_id
            self.kw['title'] = old_present.title
            self.kw['owner'] = old_present.owner
            self.kw['lat'] = old_present.lat
            self.kw['lng'] = old_present.lng

        self.render('submitpresent.html', **self.kw)

    def post(self, present_id):
        self.kw['title'] = self.get_argument('title', 'Whatever')
        self.kw['owner'] = self.get_argument('owner', 'Whoever')
        self.kw['lat'] = _get_float(self.get_argument('lat', '0.0'), 0.0)
        self.kw['lng'] = _get_float(self.get_argument('lng', '0.0'), 0.0)
        if self.request.files.get('presentation'):
            self.kw['presentation'] = self.request.files['presentation'][0]

        if present_id:
            # Old presentation
            q = Presentation.by_p_key(present_id, self.sql_session)
            old_present = q.scalar()
            if not old_present:
                raise self.HTTPError(404)

            q.update({
                    'title': self.kw['title'],
                    'owner': self.kw['owner'],
                    'lat': self.kw['lat'],
                    'lng': self.kw['lng']
                })
            # Old presentation doesn't request ppt file
            # Delete old ppt file
            if self.kw.get('presentation'):
                q = FileList.by_present_id(present_id, self.sql_session)
                old_file = q.scalar()
                shutil.rmtree(os.path.join(self.file_folder, old_file.key))
                FileList.by_present_id(present_id, self.sql_session).delete()
        else:
            # New presentation
            # New presentation requests ppt file
            if not self.kw.get('presentation'):
                raise self.HTTPError(400)

            new_present = Presentation(**self.kw)
            self.sql_session.add(new_present)
            self.sql_session.flush()
            self.sql_session.refresh(new_present)
            present_id = new_present.p_key

        # Add new ppt file
        if self.kw.get('presentation'):
            m = _file_type_re.match(self.kw['presentation']['filename'])
            if not m or not (m.group(2) in ['pptx','ppt']):
                raise self.HTTPError(400)
            self.kw['presentation']['key'] = uuid.uuid1().hex
            self.kw['presentation']['filename'] = m.group(1)
            self.kw['presentation']['file_type'] = m.group(2)
            self.kw['presentation']['present_id'] = present_id

            new_file = FileList(**self.kw['presentation'])
            file_hash_folder = os.path.join(self.file_folder, new_file.key)
            if os.path.exists(file_hash_folder):
                raise self.HTTPError(500)
            os.makedirs(file_hash_folder)
            real_file_name = os.path.join(file_hash_folder, '%s.%s' % (new_file.filename, new_file.file_type))
            with open(real_file_name, 'wb') as f:
                f.write(self.kw['presentation']['body'])
            # Convert ppt or pptx to odp
            subprocess.call('unoconv -f odp \'%s\'' % real_file_name, shell=True)

            self.sql_session.add(new_file)

        self.sql_session.commit()
        self.redirect('/present/%s' % present_id)

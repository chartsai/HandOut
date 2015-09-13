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
import time
import json
from decimal import Decimal
from threading import Thread
# import mimetypes
# from datetime import datetime

import tornado.gen

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

DEFAULT_LAT = 25.0724763
DEFAULT_LNG = 121.5185635

class QueryPresentHandler(BaseHandler):
    def get(self, api_type):
        # TODO: Get data

        self.lat = RAD_K * Decimal.from_float(_get_float(self.get_argument('lat', ''), DEFAULT_LAT))
        self.lng = RAD_K * Decimal.from_float(_get_float(self.get_argument('lng', ''), DEFAULT_LNG))

        # TODO: Query out less point
        presents = self.sql_session.query(Presentation).all()
        final_presents = []
        for present in presents:
            lat2 = RAD_K*present.lat
            lng2 = RAD_K*present.lng
            d = self._distance(lat2, lng2)
            if d < 1000:
                present.distance_string = '%d m' % d
            elif d<=5000:
                present.distance_string = '%.2f km' % float(d)/1000
            else:
                continue
            
            upload_file = FileList.by_present_id(present.p_key, self.sql_session).scalar()
            present.file_url = '/download/' + upload_file.key + '/' + upload_file.filename + '.' + upload_file.file_type
            present.img_url = '/download/' + upload_file.key + '/' + upload_file.filename + '.png'
            final_presents.append(present)
        if api_type == None:
            self.render('querypresent.html', presents = final_presents)
        elif api_type[1:] == 'json':
            return_data = []
            for present in final_presents:
                return_data.append({
                    'title': present.title,
                    'owner': present.owner,
                    'distance': present.distance_string,
                    'created': present.created.strftime("%Y-%m-%d %H:%M"),
                    'updated': present.updated.strftime("%Y-%m-%d %H:%M"),
                    'file_url': present.file_url,
                    'img_url': present.img_url,
                    'lat': str(present.lat),
                    'lng': str(present.lng)}
                )
            self.write(json.dumps(return_data))
        else:
            raise self.HTTPError(500, 'Unknown api type')

    def _distance(self, lat2, lng2):
        a = abs(self.lat - lat2)
        b = abs(self.lng - lng2)
        s = 2*math.asin(math.sqrt(math.pow(math.sin(a/2),2)+math.cos(self.lat)*math.cos(lat2)*math.pow(math.sin(b/2),2)))
        d = EARTH_R*Decimal.from_float(s)
        d_i = d.to_integral()
        return d_i

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

    @tornado.gen.coroutine
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
            if not m or not (m.group(2) in ['pptx','ppt','pdf','odp']):
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
            if m.group(2) != 'odp':
                cmd_thread = _async_command('unoconv -f odp \'%s\'' % real_file_name)
                cmd_thread.start()
                while not cmd_thread.end:
                    yield tornado.gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + 1)
            if m.group(2) != 'pdf':
                cmd_thread = _async_command('unoconv -f pdf \'%s\'' % real_file_name)
                cmd_thread.start()
                while not cmd_thread.end:
                    yield tornado.gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + 1)
            real_file_base_name = os.path.join(file_hash_folder, new_file.filename)
            cmd_thread = _async_command('convert -density 150 \'%s.pdf[0]\' -quality 90 \'%s.png\'' % (real_file_base_name, real_file_base_name))
            cmd_thread.start()
            while not cmd_thread.end:
                yield tornado.gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + 1)

            self.sql_session.add(new_file)

        self.sql_session.commit()
        self.redirect('/present/%s' % present_id)


class _async_command(Thread):
    def __init__(self, cmd):
        Thread.__init__(self)
        self.cmd = cmd
        self.end = False
        self.setName(cmd)
    def run(self):
        subprocess.call(self.cmd, shell=True)
        self.end = True

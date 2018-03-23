# -*- coding: utf-8 -*-

# Copyright (c) 2018 Digital Catapult

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals
from wstore.store_commons.database import get_database_connection
from pymongo import *

class tokenStore:
    _db = None

    def __init__(self):
        self._db = get_database_connection()
        #self._db.access_token.drop_index()
        # self._db.access_token.create_index([('appId', ASCENDING), 
        #                                     ('userId', ASCENDING)],
        #                                     unique=True
        #                                     )

    def push(self, data):
        #key = data['appId'] + ":" + data['userId']
        res = self._db.access_token.find_one_and_update(
            filter={'appId': data['appId'],
                    'userId': data['userId']},
            update={'$set': {'appId': data['appId'],
                        'userId': data['userId'],
                        'authToken': data['authToken'],
                        'refreshToken': data['refreshToken'],
                        'expire':data['expire']}},
            upsert= True
            )
        return res

    def get(self, data):
        #key = data['appId'] + ":" + data['userId']
        res = self._db.access_token.find_one(
            filter={'appId': data['appId'],
                    'userId': data['userId']}
            )
        if res is None:
            res = {}                                 
        return res
# -*- coding: utf-8 -*-

# Copyright (c) 2013 - 2016 CoNWeT Lab., Universidad Politécnica de Madrid

# This file belongs to the business-charging-backend
# of the Business API Ecosystem.

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

import json

from django.http import HttpResponse

from wstore.store_commons.utils.http import authentication_required
from wstore.store_commons.utils.units import supported_currencies
from wstore.store_commons.resource import Resource


class CurrencyCollection(Resource):

    @authentication_required
    def read(self, request):
        response = json.dumps(supported_currencies)
        return HttpResponse(response, status=200, mimetype='application/json; charset=utf-8')

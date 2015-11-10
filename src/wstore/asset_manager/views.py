# -*- coding: utf-8 -*-

# Copyright (c) 2013 - 2015 CoNWeT Lab., Universidad Politécnica de Madrid

# This file is part of WStore.

# WStore is free software: you can redistribute it and/or modify
# it under the terms of the European Union Public Licence (EUPL)
# as published by the European Commission, either version 1.1
# of the License, or (at your option) any later version.

# WStore is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# European Union Public Licence for more details.

# You should have received a copy of the European Union Public Licence
# along with WStore.
# If not, see <https://joinup.ec.europa.eu/software/page/eupl/licence-eupl>.

from __future__ import unicode_literals

import json

from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from wstore.store_commons.resource import Resource
from wstore.store_commons.utils.http import build_response, get_content_type, supported_request_mime_types, \
    authentication_required
from wstore.asset_manager.resources_management import get_provider_resources, upload_asset
from wstore.asset_manager.product_validator import ProductValidator
from wstore.store_commons.errors import ConflictError
from wstore.asset_manager.errors import ProductError


class ResourceCollection(Resource):

    @authentication_required
    def read(self, request):
        """
        Retrives the existing digital assets associated with a given seller
        :param request:
        :return: JSON List containing the existing assets
        """

        pagination = {
            'start': request.GET.get('start', None),
            'limit': request.GET.get('limit', None)
        }
        if pagination['start'] is None or pagination['limit'] is None:
            pagination = None

        profile = request.user.userprofile

        if 'provider' not in profile.get_current_roles():
            return build_response(request, 403, 'Forbidden')

        try:
            response = get_provider_resources(request.user, pagination=pagination)
        except Exception, e:
            return build_response(request, 400, unicode(e))

        return HttpResponse(json.dumps(response), status=200, mimetype='application/json; charset=utf-8')


class UploadCollection(Resource):

    @supported_request_mime_types(('application/json', 'multipart/form-data'))
    @authentication_required
    def create(self, request):
        """
        Uploads a new downloadable digital asset
        :param request:
        :return: 201 Created, including the new URL of the asset in the location header
        """

        user = request.user
        profile = user.userprofile
        content_type = get_content_type(request)[0]

        if 'provider' not in profile.get_current_roles():
            return build_response(request, 403, "You don't have the seller role")

        try:
            if content_type == 'application/json':
                data = json.loads(request.body)
                location = upload_asset(user, data)
            else:
                data = json.loads(request.POST['json'])
                f = request.FILES['file']
                location = upload_asset(user, data, file_=f)

        except ConflictError as e:
            return build_response(request, 409, unicode(e))
        except Exception as e:
            return build_response(request, 400, unicode(e))

        # Fill location header with the URL of the uploaded digital asset
        headers = {
            'Location': location
        }
        return build_response(request, 201, 'Created', headers=headers)


class ValidateCollection(Resource):

    @supported_request_mime_types(('application/json',))
    @authentication_required
    def create(self, request):
        """
        Validates the digital assets contained in a TMForum product Specification
        :param request:
        :return:
        """

        # Validate user permissions
        user = request.user
        if 'provider' not in user.userprofile.get_current_roles():
            return build_response(request, 403, "You don't have the seller role")

        product_validator = ProductValidator()

        # Parse content
        try:
            data = json.loads(request.body)
        except:
            return build_response(request, 400, 'The content is not a valid JSON document')

        if 'action' not in data:
            return build_response(request, 400, 'Missing required field: action')

        if 'product' not in data:
            return build_response(request, 400, 'Missing required field: product')

        try:
            product_validator.validate(data['action'], user.userprofile.current_organization, data['product'])
        except ValueError as e:
            return build_response(request, 400, unicode(e))
        except ProductError as e:
            return build_response(request, 400, unicode(e))
        except PermissionDenied as e:
            return build_response(request, 409, unicode(e))
        except Exception:
            return build_response(request, 400, 'Invalid product specification content')

        return build_response(request, 200, 'OK')
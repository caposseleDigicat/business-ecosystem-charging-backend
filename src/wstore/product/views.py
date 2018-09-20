# -*- coding: utf-8 -*-

# Copyright (c) 2018 Digital Catapult

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
import requests
import base64

from django.http import HttpResponse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.contrib.auth.models import User
from wstore.asset_manager.resource_plugins.plugin_error import PluginError

from wstore.models import UserProfile
from wstore.store_commons.resource import Resource
from wstore.store_commons.utils.http import build_response, get_content_type, supported_request_mime_types, \
    authentication_required
from wstore.asset_manager.asset_manager import AssetManager
from wstore.asset_manager.product_validator import ProductValidator
from wstore.asset_manager.offering_validator import OfferingValidator
from wstore.store_commons.errors import ConflictError
from wstore.asset_manager.errors import ProductError
from wstore.token.keystone_client import KeystoneClient
from .config import *
import product_spec


class ProductSpecification(Resource):
    @supported_request_mime_types(('application/json'))
    @authentication_required
    def create(self, request):
        """
        Creates a new product specification
        :param request:
        :return: JSON containing the new product specification
        """

        upload_api = "charging/api/assetManagement/assets/uploadJob"
        product_validation = "charging/api/assetManagement/assets/validateJob"
        product_specification = "DSProductCatalog/api/catalogManagement/v2/productSpecification"

        response = {}
        proxy_url = AUTHORIZE_SERVICE
        m_token = str(request.META.get('HTTP_AUTHORIZATION'))
        m_token = m_token.replace('Bearer ', '')
        body = json.loads(request.body)        
            
        data_source_id = body['dataSourceID']
            
        
        #token_store = tokenStore()
        keystone_client = KeystoneClient(KEYSTONE_USER, KEYSTONE_PWD, ADMIN_DOMAIN, KEYSTONE_PROTOCOL, KEYSTONE_HOST, KEYSTONE_PORT)
        url = APP_URL + data_source_id + '?type=ttn-device'
        try:
            token_info = keystone_client.get_token_info(m_token)        
            headers = {'Content-type': 'application/json', 'Authorization': 'Bearer ' + m_token}
            # r = requests.post(url, data=data, headers=headers)

            # #Check if token has been correctly created
            # if r.status_code != 200:
            #     return build_response(request, 401, 'Invalid password')
            # # Send the API key to the proxy using the authorizing API
            # acc_json = {
            #     'appId': application_id,
            #     'userId': user_id,
            #     'authToken': r.json()['access_token'],
            #     'refreshToken': r.json()['refresh_token'],
            #     'expire': r.json()['expires_in']
            # }

            # headers = {'Content-type': 'application/json', 'Authorization': str(request.META.get('HTTP_AUTHORIZATION'))}
            # acc_resp = requests.post(proxy_url, json=acc_json, headers=headers)

            # if acc_resp.status_code != 200:
            #     return build_response(request, 500, 'The accounting service has failed saving the token')
            # # try:
            # #     token_store.push(acc_json)
            # # except Exception as e:
            # #     return build_response(request, 500, unicode(e.message))
            # response = r.json()
            validation = product_spec.validation
            pr_sp = product_spec.template
            fiware_service = product_spec.fiware_service
            asset_type =product_spec.asset_type
            media_type = product_spec.media_type
            location = product_spec.location
            location['productSpecCharacteristicValue'][0]['value'] = url

            appId = product_spec.appId
            appId['productSpecCharacteristicValue'][0]['value'] = APP_CLIENT_ID

            pr_sp["productSpecCharacteristic"] = [fiware_service, asset_type, media_type, location, appId]
            validation["product"] = pr_sp

            pr_sp["relatedParty"][0]["id"] = token_info["id"]
            pr_sp["relatedParty"][0]["href"] = SITE + "/DSPartyManagement/api/partyManagement/v2/individual/" + token_info["id"]
            pr_sp["name"] = body["dataSourceID"]
            pr_sp["brand"] = token_info["id"]


            asset_json = {
                "resourceType":"Orion Query",
                "content":url,
                "contentType":"NGSIv2",
                "metadata":{
                    "application_id": APP_CLIENT_ID
                }
            }

            resp = requests.post(SITE + upload_api, json=asset_json, headers=headers)
            resp = requests.post(SITE + product_validation, json=validation, headers=headers)
            resp = requests.post(SITE + product_specification, json=pr_sp, headers=headers)

        except Exception as e:
            return build_response(request, 500, unicode(e))

        return HttpResponse(resp, status=200, mimetype='application/json; charset=utf-8')
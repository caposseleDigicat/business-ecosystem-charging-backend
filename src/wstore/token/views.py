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
from .keystone_client import KeystoneClient
from .tokenStore import tokenStore
from .config import *

class TokenCollection(Resource):
    @supported_request_mime_types(('application/json'))
    @authentication_required
    def create(self, request):
        """
        Creates a new OAuth2 token
        :param request:
        :return: JSON containing the new OAuth2 token
        """
        response = {}
        proxy_url = "http://proxy.docker:8004/authorizeservice"
        m_token = str(request.META.get('HTTP_AUTHORIZATION'))
        m_token = m_token.replace('Bearer ', '')
        body = json.loads(request.body)        
        try:
            username = body['username']
            password = body['password']
        except Exception as e:
            return build_response(request, 400, 'Invalid request')

        #token_store = tokenStore()
        keystone_client = KeystoneClient(KEYSTONE_USER, KEYSTONE_PWD, ADMIN_DOMAIN, 'http', 'idm.docker')

        try:
            token_info = keystone_client.get_token_info(m_token)
            user_info = keystone_client.get_user_by_name(username)
    
            if not len(user_info['users']):
                return build_response(request, 401, 'Invalid username')
            
            for user in user_info['users']:
                user_id = user['id']
            
            if token_info['id'] != user_id:
                return build_response(request, 401, 'username does not match authentication')
            
            authorization = "Basic " + str(base64.b64encode(APP_CLIENT_ID + ":" + APP_CLIENT_SECRET))
            url = KEYSTONE_HOST + ":" + KEYROCK_PORT + "/oauth2/token"
            data = "grant_type=password&username=" + username + "&password=" + password
            headers = {'Content-type': 'application/x-www-form-urlencoded', 'Authorization': authorization}
            r = requests.post(url, data=data, headers=headers)

            #Check if token has been correctly created
            if r.status_code != 200:
                return build_response(request, 401, 'Invalid password')
            # Send the API key to the proxy using the authorizing API
            acc_json = {
                'appId': APP_CLIENT_ID,
                'userId': user_id,
                'authToken': r.json()['access_token'],
                'refreshToken': r.json()['refresh_token'],
                'expire': r.json()['expires_in']
            }

            headers = {'Content-type': 'application/json', 'Authorization': str(request.META.get('HTTP_AUTHORIZATION'))}
            acc_resp = requests.post(proxy_url + '/token', json=acc_json, headers=headers)

            if acc_resp.status_code != 200:
                return build_response(request, 500, 'The accounting service has failed saving the token')
            # try:
            #     token_store.push(acc_json)
            # except Exception as e:
            #     return build_response(request, 500, unicode(e.message))
            response = r.json()
        except Exception as e:
            return build_response(request, 500, unicode(e))

        return HttpResponse(json.dumps(response), status=200, mimetype='application/json; charset=utf-8')

class TokenRead(Resource):
    @supported_request_mime_types(('application/json'))
    @authentication_required
    def create(self, request):
        response = {}
        m_token = str(request.META.get('HTTP_AUTHORIZATION'))
        m_token = m_token.replace('Bearer ', '')
        body = json.loads(request.body)        
        try:
            userId = body['userId']
            appId = body['appId']
        except Exception as e:
            return build_response(request, 400, 'Invalid request')
        
        token_store = tokenStore()
        keystone_client = KeystoneClient(KEYSTONE_USER, KEYSTONE_PWD, ADMIN_DOMAIN, 'http', 'idm.docker')

        try:
            token_info = keystone_client.get_token_info(m_token)
            user_info = keystone_client.get_user_by_username(userId)
    
            if not len(user_info['users']):
                return build_response(request, 401, 'Invalid username')
            
            for user in user_info['users']:
                user_id = user['id']
            
            if token_info['id'] != user_id:
                return build_response(request, 401, 'username does not match authentication')
            try:
                
                r = token_store.get(body)
                if not len(r):
                    response = {}
                # if r["appId"] == "test":
                #     response = r
                else:              
                    response = {
                        'appId': r['appId'],
                        'userId': r['userId'],
                        'authToken': r['authToken'],
                        'refreshToken': r['refreshToken'],
                        'expire': r['expire']
                    }
            except Exception as e:
                return build_response(request, 500, unicode(e.message))

        except Exception as e:
            return build_response(request, 500, unicode(e))

        return HttpResponse(json.dumps(response), status=200, mimetype='application/json; charset=utf-8')

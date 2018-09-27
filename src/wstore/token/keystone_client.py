# -*- coding: utf-8 -*-

# Copyright (c) 2017 CoNWeT Lab., Universidad Politécnica de Madrid

# This file belongs to the secured orion plugin
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

import requests


class KeystoneClient:

    _access_token = None
    _server = None
    _domain = None

    def __init__(self, user, password, domain, protocol, host, port=5000):
        self._domain = domain
        self._server = protocol + '://' + host + ':' + unicode(port)
        self._access_token = self._login(user, password)

    def _login(self, user, password):
        url = self._server + '/v1/auth/tokens'

        login_resp = requests.post(url, json= 
            {
            "name": user,
            "password": password
            }
        )


        login_resp.raise_for_status()
        return login_resp.headers.get('X-Subject-Token', '')

    def _make_get_request(self, url):
        resp = requests.get(url, headers={
            'X-Auth-Token': self._access_token
        })

        resp.raise_for_status()
        return resp.json()

    # def get_project_by_name(self, project_name):
    #     return self._make_get_request(self._server + '/v3/projects?name=' + project_name)

    def get_application_by_id(self, application_id):
        return self._make_get_request(self._server + '/v1/applications/' + application_id)

    # def get_domain_id(self, domain_name):
    #     resp = self._make_get_request(self._server + '/v3/domains?name=' + domain_name)
    #     for domain_id in resp['domains']:
    #         return domain_id['id']
    # def get_role_by_name(self, role_name):
    #     return self._make_get_request(self._server + '/v3/roles?name=' + role_name)

    def get_role_by_name(self, application_id, role_name ):
        res = self._make_get_request(self._server + '/v1/applications/'+application_id+'/roles')
        for role in res['roles']:
            if role['name'] == role_name:
               return role['id'] 
        return None

    # def get_user_by_name(self, username):
    #     return self._make_get_request(self._server + '/v3/users?name=' + username)

    def get_user_by_username(self, username):
        res = self._make_get_request(self._server + '/v1/users')
        for user in res['users']:
            if user['username'] == username:
               return user['id'] 
        return None
    
    def get_token_info(self, token):
        return self._make_get_request(self._server + '/user?access-token=' + token)

    def check_role(self, application_id, user_id, role_id):
        #get roles for user on application
        resp = self._make_get_request(self._server + '/v1/applications/'+application_id+'/users')
        for role in resp['role_user_assignments']:
            if role['user_id'] == user_id and role['role_id'] == role_id:
                return True
        return False 

    def create_role(self, application_id, role):
        resp = requests.post(self._server + '/v1/applications/'+application_id+'/roles',
                            json = role,
                            headers={'X-Auth-Token': self._access_token})
        resp.raise_for_status()
        return resp



    def grant_role(self, application_id, user_id, role_id):
        resp = requests.put(self._server + '/v1/applications/' + application_id + '/users' + user_id + '/roles/' + role_id, headers={
            'X-Auth-Token': self._access_token
        })
        resp.raise_for_status()

    def revoke_role(self, application_id, user_id, role_id):
        resp = requests.delete(self._server + '/v1/applications/' + application_id + '/users' + user_id + '/roles/' + role_id, headers={
            'X-Auth-Token': self._access_token
        })
        resp.raise_for_status()  

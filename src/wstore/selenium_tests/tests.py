# -*- coding: utf-8 -*-

# Copyright (c) 2013 CoNWeT Lab., Universidad Politécnica de Madrid

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

import os
import json
import shutil
import rdflib
import time

from mock import MagicMock
from nose_parameterized import parameterized
from threading import Timer

from django.conf import settings
from django.contrib.auth.models import User

from wstore.store_commons.utils.testing import save_indexes, restore_indexes, save_tags, restore_tags
from wstore.search.search_engine import SearchEngine
from wstore.selenium_tests.testcase import WStoreSeleniumTestCase
from wstore.offerings.offerings_management import _create_basic_usdl
from wstore.models import Offering, Purchase
from wstore.social.tagging.tag_manager import TagManager
from wstore.repository_adaptor import repositoryAdaptor
from wstore.selenium_tests.test_server import TestServer


TESTING_PORT = 8989

def _fill_offering_description(pk, usdl_info, owner):
    offering = Offering.objects.get(pk=pk)

    usdl = _create_basic_usdl(usdl_info)
    graph = rdflib.Graph()
    graph.parse(data=usdl, format='application/rdf+xml')
    offering.offering_description = json.loads(graph.serialize(format='json-ld', auto_compact=True))
    offering.owner_organization = User.objects.get(username=owner).userprofile.current_organization
    offering.save()


def _fill_purchase_org(pk, owner):
    user = User.objects.get(username=owner)
    purchase = Purchase.objects.get(pk=pk)

    user.userprofile.offerings_purchased.append(purchase.offering.pk)
    user.userprofile.save()

    purchase.owner_organization = user.userprofile.current_organization
    purchase.save()


def _fill_provider_role(username):
    user = User.objects.get(username=username)
    orgs = user.userprofile.organizations

    new_org = []
    for o in orgs:
        if o['organization'] == user.userprofile.current_organization.pk:
            o['roles'].append('provider')

        new_org.append(o)

    user.userprofile.organizations = new_org
    user.userprofile.save()


def _create_indexes():
    index_path = os.path.join(settings.BASEDIR, 'wstore')
    index_path = os.path.join(index_path, 'search')
    index_path = os.path.join(index_path, 'indexes')

    search_engine = SearchEngine(index_path)

    for off in Offering.objects.all():
        search_engine.create_index(off)


def _create_tags():
    tm = TagManager()
    offering1 = Offering.objects.get(name='test_offering1')
    offering2 = Offering.objects.get(name='test_offering2')
    offering3 = Offering.objects.get(name='test_offering3')

    tm.update_tags(offering1, ['service', 'tag'])
    tm.update_tags(offering2, ['dataset', 'tag'])
    tm.update_tags(offering3, ['widget'])


class BasicSearchTestCase(WStoreSeleniumTestCase):

    tags = ('selenium', )
    _dirs_to_remove = []

    def __init__(self, methodName='runTest'):
        WStoreSeleniumTestCase.__init__(self, methodName=methodName)
        self.fixtures.extend(['basic_offerings.json'])

    def setUp(self):
        # Fill offering info
        # Create test directories
        offering_path1 = os.path.join(settings.BASEDIR, 'media/provider__test_offering1__1.0')
        offering_path2 = os.path.join(settings.BASEDIR, 'media/provider__test_offering2__1.0')
        offering_path3 = os.path.join(settings.BASEDIR, 'media/provider__test_offering3__1.0')
        os.makedirs(offering_path1)
        os.makedirs(offering_path2)
        os.makedirs(offering_path3)

        self._dirs_to_remove.append(offering_path1)
        self._dirs_to_remove.append(offering_path2)
        self._dirs_to_remove.append(offering_path3)

        test_icon_path = os.path.join(settings.BASEDIR, 'wstore/defaulttheme/static/assets/img/noimage.png')
        shutil.copy2(test_icon_path, os.path.join(offering_path1, 'image.png'))
        shutil.copy2(test_icon_path, os.path.join(offering_path2, 'image.png'))
        shutil.copy2(test_icon_path, os.path.join(offering_path3, 'image.png'))

        # Load USDL info
        offering1_info = {
            'base_uri': 'http://localhost:8081',
            'image_url': '/media/provider__test_offering1__1.0/image.png',
            'name': 'test_offering1',
            'description': 'test',
            'pricing': {
                'price_model': 'free'
            }
        }
        _fill_offering_description('21000aba8e05ac2115f022ff', offering1_info, 'provider')

        offering2_info = {
            'base_uri': 'http://localhost:8081',
            'image_url': '/media/provider__test_offering2__1.0/image.png',
            'name': 'test_offering2',
            'description': 'example',
            'pricing': {
                'price_model': 'free'
            }
        }
        _fill_offering_description('31000aba8e05ac2115f022f0', offering2_info, 'provider')

        offering3_info = {
            'base_uri': 'http://localhost:8081',
            'image_url': '/media/provider__test_offering3__1.0/image.png',
            'name': 'test_offering3',
            'description': 'example offering 3',
            'pricing': {
                'price_model': 'free'
            }
        }
        _fill_offering_description('aaaaaaaaaaaaac2115f022f0', offering3_info, 'admin')
        _fill_purchase_org('61006aba8e05ac21bbbbbbbb', 'provider')

        _fill_provider_role('provider')
        # Create indexes
        save_indexes()
        _create_indexes()

        # Create tag indexes
        save_tags()
        _create_tags()

        WStoreSeleniumTestCase.setUp(self)

    def tearDown(self):
        # Remove directories
        for path in self._dirs_to_remove:
            try:
                files = os.listdir(path)
                for f in files:
                    file_path = os.path.join(path, f)
                    os.remove(file_path)

                os.rmdir(path)
            except:
                pass
        restore_indexes()
        restore_tags()
        WStoreSeleniumTestCase.tearDown(self)

    def test_offering_search(self):
        # Start interactions with the GUI
        self.login()
        self.view_all()

        # Search by keyword
        self._check_container('search-container', ['test_offering1', 'test_offering2', 'test_offering3'])
        self.assertEquals(self.driver.current_url, 'http://localhost:8081/search')

        self.search_keyword('test')

        self._check_container('search-container', ['test_offering1'])
        self.assertEquals(self.driver.current_url, 'http://localhost:8081/search/keyword/test')

        self.open_offering_details('test_offering1')

        self.back()

        # Search by main categories
        time.sleep(3)
        self.click_first_cat()
        self._check_container('search-container', ['test_offering1'])

        self.click_second_cat()
        self._check_container('search-container', ['test_offering2'])

        self.click_third_cat()
        self._check_container('search-container', ['test_offering3'])

        # Search by tag
        self.view_all()

        self.open_offering_details('test_offering1')
        self.click_tag('tag')
        self._check_container('search-container', ['test_offering1', 'test_offering2'])
        
        self.logout()

    def test_catalogue_search(self):
        self.login(username='provider')

        # Open my offerings page
        self.click_first_nav()

        # Check purchased offerings
        self._check_container('offerings-container', ['test_offering3'])

        self.click_second_cat()

        # Check provided offerings
        self._check_container('offerings-container', ['test_offering1', 'test_offering2'])

        # Search by keyword
        self.search_keyword('test', id_='#cat-search-input', btn='#cat-search')
        self._check_container('offerings-container', ['test_offering1'])

        self.logout()


class AdministrationTestCase(WStoreSeleniumTestCase):
    pass


class OfferingManagementTestCase(WStoreSeleniumTestCase):

    tags = ('selenium',)

    def __init__(self, methodName='runTest'):
        WStoreSeleniumTestCase.__init__(self, methodName=methodName)
        self.fixtures.extend(['repositories.json'])

    def setUp(self):
        # Start the testing server
        self._server = TestServer()
        self._server.set_port(TESTING_PORT)
        self._server.start()
        _fill_provider_role('provider')
        WStoreSeleniumTestCase.setUp(self)

    def tearDown(self):
        self._server.stop_server()
        path = os.path.join(settings.BASEDIR, 'media/provider__test_offering__1.0')
        try:
            files = os.listdir(path)
            for f in files:
                file_path = os.path.join(path, f)
                os.remove(file_path)

            os.rmdir(path)
        except:
            pass
        WStoreSeleniumTestCase.tearDown(self)

    def test_create_offering(self):
        self.login('provider')
        self.click_first_nav()

        self._check_container('offerings-container', [])

        # Create
        self.create_offering_menu()

        self.fill_basic_offering_info({
            'name': 'test_offering',
            'version': '1.0',
            'notification': None,
            'open': False
        })

        self.driver.find_element_by_css_selector('.modal-footer > .btn').click()

        self.fill_usdl_info({
            'type': 'form',
            'description': 'A test offering',
            'price': '10',
            'legal': {
                'title': 'terms and conditions',
                'text': 'An example terms and conditions'
            }
        })

        self.driver.find_element_by_css_selector('.modal-footer > .btn').click()  # Next
        self.driver.find_element_by_css_selector('.modal-footer > .btn').click()  # Accept
        time.sleep(1)
        self.driver.find_element_by_css_selector('.modal-footer > .btn').click()  # Accept

        self.click_second_cat()
        self._check_container('offerings-container', ['test_offering'])
        
        # Update
        self.open_offering_details('test_offering')

        # Bind
        # Publish

class ResourceManagementTestCase(WStoreSeleniumTestCase):

    def __init__(self, methodName='runTest'):
        self.fixtures.extend(['resources.json'])
        WStoreSeleniumTestCase.__init__(self, methodName=methodName)

    @parameterized.expand([
    ])
    def test_register_resource(self, resource_info):
        self.login()
        self.click_first_nav()
        self.register_resource({})

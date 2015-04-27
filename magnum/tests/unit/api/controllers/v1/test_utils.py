# Copyright 2013 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock
import wsme

from magnum.api.controllers.v1 import utils
from magnum.common import exception
from magnum.common import utils as common_utils
from magnum.tests.unit.api import base

from oslo_config import cfg

CONF = cfg.CONF


class TestApiUtils(base.FunctionalTest):

    def test_validate_limit(self):
        limit = utils.validate_limit(10)
        self.assertEqual(10, 10)

        # max limit
        limit = utils.validate_limit(999999999)
        self.assertEqual(CONF.api.max_limit, limit)

        # negative
        self.assertRaises(wsme.exc.ClientSideError, utils.validate_limit, -1)

        # zero
        self.assertRaises(wsme.exc.ClientSideError, utils.validate_limit, 0)

    def test_validate_sort_dir(self):
        sort_dir = utils.validate_sort_dir('asc')
        self.assertEqual('asc', sort_dir)

        # invalid sort_dir parameter
        self.assertRaises(wsme.exc.ClientSideError,
                          utils.validate_sort_dir,
                          'fake-sort')

    @mock.patch.object(common_utils, 'is_uuid_like', return_value=True)
    def test_get_openstack_resource_by_uuid(self, fake_is_uuid_like):
        fake_manager = mock.MagicMock()
        fake_manager.get.return_value = 'fake_resource_data'
        resource_data = utils.get_openstack_resource(fake_manager,
                                                     'fake_resource',
                                                     'fake_resource_type')
        self.assertEqual('fake_resource_data', resource_data)

    @mock.patch.object(common_utils, 'is_uuid_like', return_value=False)
    def test_get_openstack_resource_by_name(self, fake_is_uuid_like):
        fake_manager = mock.MagicMock()
        fake_manager.list.return_value = ['fake_resource_data']
        resource_data = utils.get_openstack_resource(fake_manager,
                                                     'fake_resource',
                                                     'fake_resource_type')
        self.assertEqual('fake_resource_data', resource_data)

    @mock.patch.object(common_utils, 'is_uuid_like', return_value=False)
    def test_get_openstack_resource_non_exist(self, fake_is_uuid_like):
        fake_manager = mock.MagicMock()
        fake_manager.list.return_value = []
        self.assertRaises(exception.ResourceNotFound,
                          utils.get_openstack_resource,
                          fake_manager, 'fake_resource', 'fake_resource_type')

    @mock.patch.object(common_utils, 'is_uuid_like', return_value=False)
    def test_get_openstack_resource_multi_exist(self, fake_is_uuid_like):
        fake_manager = mock.MagicMock()
        fake_manager.list.return_value = ['fake_resource_data1',
                                          'fake_resource_data2']
        self.assertRaises(exception.Conflict,
                          utils.get_openstack_resource,
                          fake_manager, 'fake_resource', 'fake_resource_type')

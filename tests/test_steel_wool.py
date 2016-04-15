# Copyright 2016 Internap
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from steel_wool.steel_wool import SteelWool
from hamcrest import assert_that, is_
import mock
from novaclient.exceptions import ClientException


class AFakeInstance(object):
    def __init__(self, instance_uuid="", hypervisor_id=""):
        self.id = instance_uuid
        setattr(self, 'OS-EXT-SRV-ATTR:hypervisor_hostname', hypervisor_id)

    def __eq__(self, other):
        return vars(self) == vars(other)


class AFakeNode(object):
    def __init__(self, uuid, instance_uuid):
        self.id = uuid
        self.instance_uuid = instance_uuid

    def __eq__(self, other):
        return vars(self) == vars(other)


class SteelWoolTests(unittest.TestCase):

    def setUp(self):
        self.steel_wool = SteelWool(mock.Mock(), mock.Mock())
        self.fake_nodes = {
            'node-{}'.format(i): AFakeNode('node-{}'.format(i), 'instance-{}'.format(i))
            for i in range(1, 6)}
        self.fake_instances = {
            'instance-{}'.format(i): AFakeInstance(instance_uuid='instance-{}'.format(i))
            for i in range(1, 6)}

    def test_get_ironic_nodes_returns_successfully(self):
        self.steel_wool.ironic_client.node.get.side_effect = self.fake_nodes.get
        assert_that(
            self.steel_wool.get_ironic_nodes(['node-1', 'node-4']),
            is_([self.fake_nodes["node-1"], self.fake_nodes["node-4"]])
        )

    def test_get_ironic_nodes_raises(self):
        self.steel_wool.ironic_client.node.get.side_effect = ClientException(
            401, 'some_exc'
        )

        with self.assertRaises(ClientException):
            self.steel_wool.get_ironic_nodes(['node-1', 'node-4'])

    def test_get_instances_returns_successfully(self):
        self.steel_wool.nova_client.servers.get.side_effect = \
            self.fake_instances.get
        assert_that(
            self.steel_wool.get_instances_by_instance_ids(
                ['instance-1', 'instance-4']),
            is_([self.fake_instances["instance-1"],
                 self.fake_instances["instance-4"]])
        )

    def test_get_instances_raises(self):
        self.steel_wool.nova_client.servers.get.side_effect = ClientException(
            401, 'some_exc'
        )

        with self.assertRaises(ClientException):
            self.steel_wool.get_instances_by_instance_ids(
                ['instance-1', 'instance-4'])

    @mock.patch('steel_wool.steel_wool.SteelWool.get_ironic_nodes')
    def test_get_instance_uuids_by_nodes_is_successful(self, mock_ironic_nodes):

        mock_ironic_nodes.return_value = [
            self.fake_nodes['node-1'],
            self.fake_nodes['node-4'],
        ]

        uuids = self.steel_wool.get_instance_uuids_by_node_uuids(
            ['node-1', 'node-4'])

        self.assertEquals(uuids, ['instance-1', 'instance-4'])

    @mock.patch('steel_wool.steel_wool.SteelWool.get_ironic_nodes')
    def test_get_instance_uuids_by_nodes_does_not_store_none_as_instance_uuid(
            self, mock_ironic_nodes):

        self.fake_nodes['node-5'] = AFakeNode('node-5', instance_uuid=None)

        mock_ironic_nodes.return_value = [
            self.fake_nodes['node-1'],
            self.fake_nodes['node-4'],
            self.fake_nodes['node-5']
            ]

        uuids = self.steel_wool.get_instance_uuids_by_node_uuids(
            ['node-1', 'node-4'])

        self.assertEquals(uuids, ['instance-1', 'instance-4'])

    @mock.patch('steel_wool.steel_wool.SteelWool.get_ironic_nodes')
    def test_get_instances_uuids_by_nodes_raises(self, mock_ironic_nodes):

        mock_ironic_nodes.side_effect = ClientException(500, 'bad bad bad')

        with self.assertRaises(ClientException):
            self.steel_wool.get_instance_uuids_by_node_uuids(['node-1', 'node-4'])

    def test_deleting_instances_is_successful(self):

        m = [mock.Mock() for _ in range(3)]
        self.steel_wool.delete_instances(m)

        for i in m:
            i.delete.assert_called_once_with()

    def test_deleting_instance_raises(self):

        m = mock.Mock()
        m.delete.side_effect = ClientException(401, 'some_exc')

        with self.assertRaises(ClientException):
            self.steel_wool.delete_instances([m])


    @mock.patch('steel_wool.steel_wool.SteelWool.delete_instances')
    @mock.patch('steel_wool.steel_wool.SteelWool.get_instances_by_instance_ids')
    @mock.patch('steel_wool.steel_wool.SteelWool.get_instance_uuids_by_node_uuids')
    def test_clean_environment_is_successful(
            self,
            mock_get_inst_uuids_by_node_uuid,
            mock_get_inst_by_inst_uuids,
            mock_delete_instances,
    ):

        mock_get_inst_uuids_by_node_uuid.return_value = [
            'instance-1', 'instance-4']
        mock_get_inst_by_inst_uuids.return_value = [
            self.fake_instances.get('instance-1'),
            self.fake_instances.get('instance-4')
        ]

        self.steel_wool.clean_environment(['node-1', 'node-4'])

        mock_get_inst_uuids_by_node_uuid.assert_called_once_with(
            ['node-1', 'node-4'])
        mock_get_inst_by_inst_uuids.assert_called_once_with(
            ['instance-1', 'instance-4']
        )
        mock_delete_instances.assert_called_once_with([
            self.fake_instances.get('instance-1'),
            self.fake_instances.get('instance-4')
        ])

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

from logging import getLogger
from novaclient.exceptions import ClientException


class SteelWool(object):
    def __init__(self, nova_client, ironic_client):
        self.nova_client = nova_client
        self.ironic_client = ironic_client
        self.log = getLogger(__name__)

    def get_ironic_nodes(self, node_uuids):
        try:
            nodes = map(self.ironic_client.node.get, node_uuids)
        except ClientException as e:
            self.log.error("Error getting node: {}".format(e.message))
            raise
        return nodes

    def get_instances_by_instance_ids(self, instance_uuids):
        try:
            instances = map(self.nova_client.servers.get, instance_uuids)
        except ClientException as e:
            self.log.error("Error getting instances: {}".format(e.message))
            raise
        return instances

    def get_instance_uuids_by_node_uuids(self, node_uuids):
        return [
            i.instance_uuid
            for i in self.get_ironic_nodes(node_uuids)
            if i.instance_uuid]

    def delete_instances(self, instances):
        try:
            for instance in instances:
                self.log.info("Deleting instance: {}".format(instance.id))
                instance.delete()
        except ClientException as e:
            self.log.error("Error Deleting instance: {}".format(e.message))
            raise

    def clean_environment(self, node_uuids):
        instance_uuids = self.get_instance_uuids_by_node_uuids(node_uuids)
        self.log.debug("Instance uuids found: {}".format(instance_uuids))
        instances = self.get_instances_by_instance_ids(instance_uuids)
        self.delete_instances(instances)

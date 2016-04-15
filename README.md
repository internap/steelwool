Steelwool
======

Steelwool is a helper tool to faciliate the cleaning of instances on ironic nodes.

Python code usage
-----------------

```python
from steel_wool.steel_wool import SteelWool
from ironicclient.client import get_client
from novaclient.v2 import client

# Configure a nova_client
nova_client = client.Client(
        username=USERNAME,
        api_key=PASSWORD,
        project_id=TENANT_NAME,
        auth_url=KEYSTONE_ENDPOINT + '/v2.0',
        region_name=REGION_NAME,
        service_type="compute")

# Configure a ironic_client              
ironic_client = get_client(
        api_version='1',
        os_tenant_name=TENANT_NAME,
        os_username=USERNAME,
        os_password=PASSWORD,
        os_auth_url=KEYSTONE_ENDPOINT + '/v2.0',
        os_auth_token='')

# Start Cleaning Baremetal Nodes
metal_cleaner = SteelWool(nova_client, ironic_client)
metal_cleaner.clean_environment(['node_uuid_1', 'node_uuid_2'])
```

Running Test Framework
-----------------

Within the project root, simply run: 

```bash
tox -r
```


Contributing
============

Feel free to raise issues and send some pull request, we'll be happy to look at them!

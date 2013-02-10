# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
eNoCloud driver
"""
from libcloud.compute.types import Provider, LibcloudError
from libcloud.compute.base import NodeLocation
from libcloud.compute.drivers.openstack import OpenStack_1_0_Connection,\
    OpenStack_1_0_NodeDriver, OpenStack_1_0_Response
from libcloud.compute.drivers.openstack import OpenStack_1_1_Connection,\
    OpenStack_1_1_NodeDriver


# To be fixed AUTH_URL_FR
AUTH_URL_FR = 'http://198.154.188.142:5000/v2.0'
AUTH_URL_CA = 'http://198.154.188.142:5000/v2.0'


ENDPOINT_ARGS_MAP = {
    'ca': {'service_type': 'compute',
           'name': 'cloudServersOpenStack',
           'region': 'sirius.ca.enocloud.com'},
    'fr': {'service_type': 'compute',
           'name': 'cloudServersOpenStack',
           'region': 'TBD'},
}


class EnocloudConnection(OpenStack_1_1_Connection):
    """
    Connection class for the eNoCloud OpenStack base driver.
    """
    get_endpoint_args = {}

    def __init__(self, user_id, key, *args, **kwargs):
        super(EnocloudConnection, self).__init__(user_id, key, *args, **kwargs)

        # regions are hardcoded
        if self.auth_url == AUTH_URL_CA:
            self._ex_force_service_region = 'sirius.ca.enocloud.com'

        # default tenant is the user_id
        if not self._ex_tenant_name:
            self._ex_tenant_name = user_id

    def get_endpoint(self):
        if not self.get_endpoint_args:
            raise LibcloudError(
                'EnocloudConnection must have get_endpoint_args set')
            
        ep = self.service_catalog.get_endpoint(service_type='compute',
                                               name='nova',
                                               region=self._ex_force_service_region)
        
        if 'publicURL' in ep:
            return ep['publicURL']
        
        raise LibcloudError('Could not find specified endpoint')


class EnocloudNodeDriver(OpenStack_1_1_NodeDriver):
    name = 'eNoCloud'
    website = 'http://www.enocloud.com'
    connectionCls = EnocloudConnection
    type = Provider.ENOCLOUD
    api_name = None

    def __init__(self, key, secret=None, secure=False, host=None, port=None,
                 datacenter='ca', **kwargs):
        """
        @inherits:  L{NodeDriver.__init__}

        @param datacenter: Datacenter ID which should be used
        @type datacenter: C{str}
        """
        
        if datacenter not in ['fr', 'ca']:
            raise ValueError('Invalid datacenter: %s' % (datacenter))

        if datacenter in ['ca', ]:
            self.connectionCls.auth_url = AUTH_URL_CA
        elif datacenter == 'fr':
            self.connectionCls.auth_url = AUTH_URL_FR

        self.connectionCls._auth_version = '2.0_password'
        self.connectionCls.get_endpoint_args = \
            ENDPOINT_ARGS_MAP[datacenter]

        self.datacenter = datacenter

        super(EnocloudNodeDriver, self).__init__(key=key, secret=secret,
                                                 secure=secure, host=host,
                                                 port=port, **kwargs)

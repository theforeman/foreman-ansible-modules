#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017, Ismael Puerto <ipuertofreire@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: foreman_host
short_description: Create or update host
description:
    - Allows the upload of content to a Katello repository
author: "Ismael Puerto (@ismaelpuerto)"
requirements:
    - "nailgun >= 0.28.0"
    - "python >= 2.6"
options:
    server_url:
        description:
            - URL of Foreman server
        required: true
    username:
        description:
            - Username on Foreman server
        required: true
    password:
        description:
            - Password for user accessing Foreman server
        required: true
    verify_ssl:
        description:
            - Verify SSL of the Foreman server
        required: false
    hostname:
        description:
            - Hostname
        required: true
    mac:
        description:
            - MAC HOST
        required: true
    organization:
        description:
            - Organization
        required: true
    location:
        description:
            - Location
        required: true
    architecture
        description:
            - Architecture
        required: true
    operatingsystem
        description:
            - Operating System
        required: true
'''

EXAMPLES = '''
- name: "Create Host"
  foreman_host:
    username: "admin"
    password: "admin"
    server_url: "https://foreman.example.com"
    hostname: "hostname"
    mac: "00:00:00:00:00:00"
    organization: "Default Organization"
    location: "Default Location"
    architecture: "x86_64"
    operatingsystem: "Fedora 26"
  delegate_to: localhost
'''

RETURN = '''# '''

try:
    from nailgun import entities, entity_fields, entity_mixins
    from nailgun.config import ServerConfig
    HAS_NAILGUN_PACKAGE = True
except:
    HAS_NAILGUN_PACKAGE = False


class NailGun(object):

    def __init__(self, server, entities, module):
        self._server = server
        self._entities = entities
        self._module = module
        entity_mixins.TASK_TIMEOUT = 1000


    def create_host(self, hostname, mac, organization, location, architecture, operatingsystem):
        location_id = self.find_location(location)
        organization_id = self.find_organization(organization)
        architecture_id = self.find_architecture(architecture)
        operatingsystem_id = self.find_operatingsystem(operatingsystem)

        host = self._entities.Host(self._server, name=hostname, organization=organization_id, location=location_id, mac=mac, architecture=architecture_id, operatingsystem=operatingsystem_id)
        response = host.search(set(), {'search': 'name={}'.format(hostname)})
        if len(response) == 0:
            host.create()
        else:
            #host_id = response[0]
            host_id = response[0]
            host = self._entities.Host(self._server, name=hostname, id=host_id.id, organization=organization_id, location=location_id, mac=mac, architecture=architecture_id, operatingsystem=operatingsystem_id)
            host.update()

    def find_operatingsystem(self, name, **params):
        os = self._entities.OperatingSystem(self._server, name=name, **params)
        response = os.search(set(), {'search': 'name={}'.format(name)})
        
        if len(response) == 1:
            return response[0]
        else:
            self._module.fail_json(msg="No operating found for %s" % name)

    def find_architecture(self, name, **params):
        org = self._entities.Architecture(self._server, name=name, **params)
        response = org.search(set(), {'search': 'name={}'.format(name)})

        if len(response) == 1:
            return response[0]
        else:
            self._module.fail_json(msg="No architecture found for %s" % name)

    def find_organization(self, name, **params):
        org = self._entities.Organization(self._server, name=name, **params)
        response = org.search(set(), {'search': 'name={}'.format(name)})

        if len(response) == 1:
            return response[0]
        else:
            self._module.fail_json(msg="No organization found for %s" % name)

    def find_location(self, name, **params):
        loc = self._entities.Location(self._server, name=name, **params)
        response = loc.search(set(), {'search': 'name={}'.format(name)})

        if len(response) == 1:
            return response[0]
        else:
            self._module.fail_json(msg="No Location found for %s" % name)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(required=False, type='bool', default=False),
            hostname=dict(required=True, no_log=False),
            mac=dict(required=True, no_log=False),
            organization=dict(required=True, no_log=False),
            location=dict(required=True, no_log=False),
            architecture=dict(required=True, no_log=False),
            operatingsystem=dict(required=True, no_log=False),
        ),
        supports_check_mode=True
    )

    if not HAS_NAILGUN_PACKAGE:
        module.fail_json(msg="Missing required nailgun module (check docs or install with: pip install nailgun")

    server_url = module.params['server_url']
    username = module.params['username']
    password = module.params['password']
    hostname = module.params['hostname']
    mac = module.params['mac']
    organization = module.params['organization']
    location = module.params['location']
    architecture = module.params['architecture']
    operatingsystem = module.params['operatingsystem']
    verify_ssl = module.params['verify_ssl']

    server = ServerConfig(
        url=server_url,
        auth=(username, password),
        verify=verify_ssl
    )
    ng = NailGun(server, entities, module)

    # Lets make an connection to the server with username and password
    try:
        org = entities.Organization(server)
        org.search()
    except Exception as e:
        module.fail_json(msg="Failed to connect to Foreman server: %s " % e)

    try:
        ng.create_host(hostname, mac, organization, location, architecture, operatingsystem)
    except Exception as e:
        module.fail_json(msg=to_native(e))

    module.exit_json(changed=True, result="Host")


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native

if __name__ == '__main__':
    main()

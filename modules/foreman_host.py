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
short_description: Manage Foreman Host
description:
    - Manage host
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
    from nailgun.entities import (
            Host,
    )
    from ansible.module_utils.ansible_nailgun_cement import (
            create_server,
            create_entity,
            update_entity,
            handle_no_nailgun,
            find_organization,
            find_operatingsystem,
            find_architecture,
            find_location,
            ping_server,
    )
    HAS_NAILGUN_PACKAGE = True
except:
    HAS_NAILGUN_PACKAGE = False

def create_host(module, hostname, mac, organization, location, architecture, operatingsystem):
    changed = False
    location_id = find_location(module, location)
    organization_id = find_organization(module, organization)
    architecture_id = find_architecture(module, architecture)
    operatingsystem_id = find_operatingsystem(module, operatingsystem)

    host = Host(name=hostname)
    host = host.search(set(), {'search': 'name="{}"'.format(hostname)})

    if len(host) == 0:
        props = { 'name': hostname, 'organization': organization_id, 'location': location_id, 'mac': mac, 'architecture': architecture_id, 'operatingsystem': operatingsystem_id }
        create_entity(Host, props, module)
        changed = True
    else:
        props = { 'name': hostname, 'organization': organization_id, 'location': location_id, 'mac': mac, 'architecture': architecture_id, 'operatingsystem': operatingsystem_id }
        update_entity(host[0], props, module)
        changed = True

    return changed

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
    )

    handle_no_nailgun(module, HAS_NAILGUN_PACKAGE)

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

    create_server(server_url, (username, password), verify_ssl)
    ping_server(module)

    try:
        changed = create_host(module, hostname, mac, organization, location, architecture, operatingsystem)
        module.exit_json(changed=changed)
    except Exception as e:
        module.fail_json(msg=to_native(e))

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native

if __name__ == '__main__':
    main()

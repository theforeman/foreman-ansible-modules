#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c)Matthias Dellweg & Bernhard Hopfenmüller 2017
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

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: foreman_ptable
short_description: Manage Partition Table Template in Foreman
description:
    - "Manage Foreman Partition Table"
    - "Uses https://github.com/SatelliteQE/nailgun"
    - "Uses ansible_nailgun_cement in /module_utils"
version_added: "2.4"
author:
- "Bernhard Hopfenmueller(@Fobhep)"
- "Matthias Dellweg (@mdellweg)"
requirements:
    - nailgun >= 0.29.0
options:
    server_url:
        description:
        - URL of Foreman server
        required: true
    username:
        description:
        - Username on Foreman server
        required: true
        default: true
    password:
        description:
        - Password for user accessing Foreman server
        required: true
    verify_ssl:
        description:
        - Verify SSL of the Foreman server
        required: false
    file_name:
        description:
        - |
            The path of a template file, that shall be imported.
            Either this or layout is required as a source for
            the Partition Template "content".
        required: false
    layout:
        description:
        - |
            The content of the provisioning template, either this or file_name
            is required as a source for the Partition Template "content".
        required: false
    locations:
        description:
        - The locations the template should be assigend to
        required: false
    name:
        description:
        - |
            The name a template should be assigned with in Foreman.
            A name must be provided.
            Possible sources are, ordererd by preference:
            The "name" parameter, config header (inline or in a file),
            basename of a file.
        required: false
    organizations:
        description:
        - The organizations the template shall be assigned to
        required: false
    os_family:
        description: The OS family the template shall be assigned with.
        required: false
        choices:
        - AIX
        - Altlinux
        - Archlinux
        - Debian
        - Freebsd
        - Gentoo
        - Junos
        - Redhat
        - Solaris
        - Suse
        - Windows
    state:
        description: The state the template should be in.
        require: true
        choices:
        - absent
        - latest
        - present

'''

EXAMPLES = '''

# Keep in mind, that in this case, the inline parameters will be overwritten
- name: "Create a Partition Table inline"
  local_action:
      module: foreman_ptable
      username: "admin"
      password: "admin"
      server_url: "https://foreman.example.com"
      name: A New Partition Template
      state: present
      layout: |
        <%#
            name: A Partition Template
        %>
        zerombr
        clearpart --all --initlabel
        autopart
      locations:
      - Gallifrey
      organizations:
      - TARDIS INC

- name: "Create a Partition Template from a file"
  local_action:
      module: foreman_ptable
      username: "admin"
      password: "admin"
      server_url: "https://foreman.example.com"
      file_name: timeywimey_template.erb
      state: present
      locations:
      - Gallifrey
      organizations:
      - TARDIS INC

- name: "Delete a Partition Template"
  local_action:
      module: foreman_ptable
      username: "admin"
      password: "admin"
      server_url: "https://foreman.example.com"
      name: timeywimey
      layout: |
        <%#
            dummy:
        %>
      state: absent

- name: "Create a Partition Template from a file and modify with parameter(s)"
  local_action:
      module: foreman_ptable
      username: "admin"
      password: "admin"
      server_url: "https://foreman.example.com"
      file_name: timeywimey_template.erb
      name: Wibbly Wobbly Template
      state: present
      locations:
      - Gallifrey
      organizations:
      - TARDIS INC

# Providing a name in this case wouldn't be very sensible.
# Alternatively make use of with_filetree to parse recursively with filter.
- name: "Parsing a directory of partition templates"
  local_action:
      module: foreman_ptable
      username: "admin"
      password: "admin"
      server_url: "https://foreman.example.com"
      file_name: "{{ item }}"
      state: present
      locations:
      - SKARO
      organizations:
      - DALEK INC
      with_fileglob:
       - "./arsenal_templates/*.erb"

'''

RETURN = ''' # '''
try:
    from nailgun.entities import (
        PartitionTable,
        OperatingSystem,
        _OPERATING_SYSTEMS,
    )

    from ansible.module_utils.ansible_nailgun_cement import (
        Organization,
        Location,
        create_server,
        find_entity,
        find_entities,
        naildown_entity_state,
        parse_template,
        parse_template_from_file,
    )
    HAS_NAILGUN_PACKAGE = True
except ImportError:
    HAS_NAILGUN_PACKAGE = False

import os
from ansible.module_utils.basic import AnsibleModule, get_module_path
from ansible.module_utils._text import to_bytes, to_native


def sanitize_ptable_dict(ptable_dict):
    # This is the only true source for names (and conversions thereof)
    name_map = {
        'layout': 'layout',
        'locations': 'location',
        'name': 'name',
        'organizations': 'organization',
        'os_family': 'os_family',
    }
    result = {}
    for key, value in name_map.iteritems():
        if key in ptable_dict:
            result[value] = ptable_dict[key]
    return result
    # Missing parameters:
    # snippet
    # locked
    # audit_comment
    # default


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            # audit_comment=dict(),
            layout=dict(),
            file_name=dict(type='path'),
            locations=dict(type='list'),
            # locked=dict(type='bool', default=False),
            name=dict(),
            organizations=dict(type='list'),
            os_family=dict(choices=list(_OPERATING_SYSTEMS)),
            state=dict(required=True, choices=['absent', 'present', 'latest']),
        ),
        supports_check_mode=True,
        mutually_exclusive=[
            ['file_name', 'layout'],
        ],
        required_one_of=[
            ['file_name', 'layout'],
        ],

    )
    if not HAS_NAILGUN_PACKAGE:
        module.fail_json(
            msg='Missing required nailgun module'
                '(check docs or install with: pip install nailgun')

    ptable_dict = dict(
        [(k, v) for (k, v) in module.params.iteritems() if v is not None])

    server_url = ptable_dict.pop('server_url')
    username = ptable_dict.pop('username')
    password = ptable_dict.pop('password')
    verify_ssl = ptable_dict.pop('verify_ssl')
    state = ptable_dict.pop('state')
    file_name = ptable_dict.pop('file_name', None)

    if file_name:
        # module params are priorized
        parsed_dict = parse_template_from_file(file_name, module)
        parsed_dict.update(ptable_dict)
        ptable_dict = parsed_dict
    elif ptable_dict['layout']:
        parsed_dict = parse_template(ptable_dict['layout'], module)
        parsed_dict.update(ptable_dict)
        ptable_dict = parsed_dict

    if 'name' not in ptable_dict:
        ptable_dict['name'] = os.path.splitext(os.path.basename(file_name))[0]

    try:
        create_server(server_url, (username, password), verify_ssl)
        entity = find_entity(PartitionTable, name=ptable_dict['name'])
    except Exception as e:
        module.fail_json(msg='Failed to connect to Foreman server: %s ' % e)

    # Set Locations of partition table
    if 'locations' in ptable_dict:
        ptable_dict['locations'] = find_entities(Location, ptable_dict[
            'locations'], module)

    # Set Organizations of partition table
    if 'organizations' in ptable_dict:
        ptable_dict['organizations'] = find_entities(
            Organization, ptable_dict['organizations'], module)

    ptable_dict = sanitize_ptable_dict(ptable_dict)

    changed = naildown_entity_state(PartitionTable, ptable_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()

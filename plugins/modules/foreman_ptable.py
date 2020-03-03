#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017 Matthias Dellweg & Bernhard Hopfenmüller (ATIX AG)
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

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: foreman_ptable
short_description: Manage Partition Table Template in Foreman
description:
    - "Manage Foreman Partition Table"
author:
  - "Bernhard Hopfenmueller (@Fobhep) ATIX AG"
  - "Matthias Dellweg (@mdellweg) ATIX AG"
options:
  file_name:
    description:
      - |
        The path of a template file, that shall be imported.
        Either this or layout is required as a source for
        the Partition Template "content".
    required: false
    type: path
  layout:
    description:
      - |
        The content of the Partitioning Table Template, either this or file_name
        is required as a source for the Partition Template "content".
    required: false
    type: str
  locked:
    description:
      - Determines whether the template shall be locked
    required: false
    type: bool
  name:
    description:
      - |
        The name a template should be assigned with in Foreman.
        A name must be provided.
        Possible sources are, ordererd by preference:
        The "name" parameter, config header (inline or in a file),
        basename of a file.
        The special name "*" (only possible as parameter) is used
        to perform bulk actions (modify, delete) on all existing partition tables.
    required: false
    type: str
  updated_name:
    description: New name of the template. When this parameter is set, the module will not be idempotent.
    required: false
    type: str
  os_family:
    description:
      - The OS family the template shall be assigned with.
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state_with_defaults
  - theforeman.foreman.foreman.taxonomy
  - theforeman.foreman.foreman.os_family
'''

EXAMPLES = '''

# Keep in mind, that in this case, the inline parameters will be overwritten
- name: "Create a Partition Table inline"
  foreman_ptable:
    username: "admin"
    password: "changeme"
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
  foreman_ptable:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    file_name: timeywimey_template.erb
    state: present
    locations:
      - Gallifrey
    organizations:
      - TARDIS INC

- name: "Delete a Partition Template"
  foreman_ptable:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: timeywimey
    layout: |
      <%#
          dummy:
      %>
    state: absent

- name: "Create a Partition Template from a file and modify with parameter(s)"
  foreman_ptable:
    username: "admin"
    password: "changeme"
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
  foreman_ptable:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    file_name: "{{ item }}"
    state: present
    locations:
      - SKARO
    organizations:
      - DALEK INC
    with_fileglob:
       - "./arsenal_templates/*.erb"

# If the templates are stored locally and the ansible module is executed on a remote host
- name: Ensure latest version of all Ptable Community Templates
  foreman_ptable:
    server_url: "https://foreman.example.com"
    username:  "admin"
    password:  "changeme"
    state: present
    layout: '{{ lookup("file", item.src) }}'
  with_filetree: '/path/to/partition/tables'
  when: item.state == 'file'


# with name set to "*" bulk actions can be performed
- name: "Delete *ALL* partition tables"
  local_action:
    module: foreman_ptable
    username: "admin"
    password: "admin"
    server_url: "https://foreman.example.com"
    name: "*"
    state: absent

- name: "Assign all partition tables to the same organization(s)"
  local_action:
    module: foreman_ptable
    username: "admin"
    password: "admin"
    server_url: "https://foreman.example.com"
    name: "*"
    state: present
    organizations:
      - DALEK INC
      - sky.net
      - Doc Brown's garage

'''

RETURN = ''' # '''


import os

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import (
    ForemanTaxonomicEntityAnsibleModule,
    parse_template,
    parse_template_from_file,
    OS_LIST,
)


class ForemanPtableModule(ForemanTaxonomicEntityAnsibleModule):
    pass


def main():
    module = ForemanPtableModule(
        argument_spec=dict(
            file_name=dict(type='path'),
            state=dict(default='present', choices=['absent', 'present_with_defaults', 'present']),
            updated_name=dict(),
        ),
        entity_spec=dict(
            layout=dict(),
            locked=dict(type='bool'),
            name=dict(),
            os_family=dict(choices=OS_LIST),
        ),
        mutually_exclusive=[
            ['file_name', 'layout'],
        ],
        required_one_of=[
            ['name', 'file_name', 'layout'],
        ],
        entity_resolve=False,
    )

    # We do not want a layout text for bulk operations
    if module.params['name'] == '*':
        if module.params['file_name'] or module.params['layout'] or module.params['updated_name']:
            module.fail_json(
                msg="Neither file_name nor layout nor updated_name allowed if 'name: *'!")

    entity = None
    entity_dict = module.clean_params()
    file_name = entity_dict.pop('file_name', None)

    if file_name or 'layout' in entity_dict:
        if file_name:
            parsed_dict = parse_template_from_file(file_name, module)
        else:
            parsed_dict = parse_template(entity_dict['layout'], module)
        parsed_dict['layout'] = parsed_dict.pop('template')
        if 'oses' in parsed_dict:
            parsed_dict['os_family'] = parsed_dict.pop('oses')
        # sanitize name from template data
        # The following condition can actually be hit, when someone is trying to import a
        # template with the name set to '*'.
        # Besides not being sensible, this would go horribly wrong in this module.
        if 'name' in parsed_dict and parsed_dict['name'] == '*':
            module.fail_json(msg="Cannot use '*' as a partition table name!")
        # module params are priorized
        parsed_dict.update(entity_dict)
        entity_dict = parsed_dict

    # make sure, we have a name
    if 'name' not in entity_dict:
        if file_name:
            entity_dict['name'] = os.path.splitext(
                os.path.basename(file_name))[0]
        else:
            module.fail_json(
                msg='No name specified and no filename to infer it.')

    affects_multiple = entity_dict['name'] == '*'
    # sanitize user input, filter unuseful configuration combinations with 'name: *'
    if affects_multiple:
        if module.state == 'present_with_defaults':
            module.fail_json(msg="'state: present_with_defaults' and 'name: *' cannot be used together")
        if module.desired_absent:
            if len(entity_dict.keys()) != 1:
                module.fail_json(msg='When deleting all partition tables, there is no need to specify further parameters.')

    with module.api_connection():
        if affects_multiple:
            entities = module.list_resource('ptables')
            if not entities:
                # Nothing to do; shortcut to exit
                module.exit_json()
            if not module.desired_absent:  # not 'thin'
                entities = [module.show_resource('ptables', entity['id']) for entity in entities]
        else:
            entity = module.find_resource_by_name('ptables', name=entity_dict['name'], failsafe=True)

        if not module.desired_absent:
            _entity, entity_dict = module.resolve_entities(entity_dict, entity)

        if not affects_multiple:
            module.ensure_entity('ptables', entity_dict, entity)
        else:
            entity_dict.pop('name')
            for entity in entities:
                module.ensure_entity('ptables', entity_dict, entity)


if __name__ == '__main__':
    main()

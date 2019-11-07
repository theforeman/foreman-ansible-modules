#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Jameer Pathan <jameerpathan111@gmail.com>
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
module: foreman_scap_content
short_description: Manage Foreman SCAP content using Foreman API.
description:
  - Create, Update and Delete Foreman SCAP content using Foreman API.
author:
  - "Jameer Pathan (@jameerpathan111)"
options:
  title:
    description: Title of SCAP content.
    required: true
    type: str
  updated_title:
    description: New SCAP content name. When this parameter is set, the module will not be idempotent.
    type: str
  scap_file:
    description: XML containing SCAP content. Required when creating SCAP content.
    required: false
    type: str
  original_filename:
    description: Original file name of the XML file
    required: false
    type: str
  locations:
    description: List of locations the SCAP content should be assigned to
    required: false
    type: list
  organizations:
    description: List of organizations the SCAP content should be assigned to
    required: false
    type: list
  state:
    description: SCAP content presence
    default: present
    choices: ["present", "absent"]
    type: str
extends_documentation_fragment: foreman
'''

EXAMPLES = '''
- name: Create SCAP content
  foreman_scap_contents:
    title: "Red Hat firefox default content"
    scap_file: "{{ lookup('file', '/home/user/Downloads/ssg-firefox-ds.xml') }}"
    original_filename: "ssg-firefox-ds.xml"
    organizations:
      - "Default Organization"
    locations:
    - "Default Location"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present
- name: Update SCAP content
  foreman_scap_contents:
    title: "Red Hat firefox default content"
    updated_title: "Updated scap content title"
    scap_file: "{{ lookup('file', '/home/user/Downloads/updated-ssg-firefox-ds.xml') }}"
    original_filename: "updated-ssg-firefox-ds.xml"
    organizations:
      - "Org One"
      - "Org Two"
    locations:
        - "Loc Tne"
        - "Loc Two"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present
- name: Delete SCAP content
  foreman_scap_contents:
    title: "Red Hat firefox default content"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: absent
'''

RETURN = ''' # '''

from ansible.module_utils.foreman_helper import ForemanEntityAnsibleModule


def main():
    module = ForemanEntityAnsibleModule(
        argument_spec=dict(
            updated_title=dict(type='str'),
        ),
        entity_spec=dict(
            title=dict(type='str', required=True),
            original_filename=dict(type='str', required=False),
            scap_file=dict(type='str'),
            organizations=dict(type='entity_list', flat_name='organization_ids'),
            locations=dict(type='entity_list', flat_name='location_ids'),
        ),
    )

    entity_dict = module.clean_params()

    module.connect()

    entity = module.find_scapcontent(entity_dict['title'], failsafe=True)

    if not module.desired_absent:
        if entity and 'updated_title' in entity_dict:
            entity_dict['title'] = entity_dict.pop('updated_title')

        if not entity and 'scap_file' not in entity_dict:
            module.fail_json(msg="Content of scap_file not provided. XML containing SCAP content is required.")

        if 'locations' in entity_dict:
            entity_dict['locations'] = module.find_resources_by_title('locations', entity_dict['locations'], thin=True)

        if 'organizations' in entity_dict:
            entity_dict['organizations'] = module.find_resources_by_name('organizations', entity_dict['organizations'], thin=True)

    changed = module.ensure_entity_state('scap_contents', entity_dict, entity)

    module.exit_json(changed=changed, entity_dict=entity_dict)


if __name__ == '__main__':
    main()

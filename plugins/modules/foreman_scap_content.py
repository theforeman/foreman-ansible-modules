#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Jameer Pathan <jameerpathan111@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: foreman_scap_content
short_description: Manage Foreman SCAP content.
description:
  - Create, update and delete SCAP content.
author:
  - "Jameer Pathan (@jameerpathan111)"
options:
  title:
    description:
      - Title of SCAP content.
    required: true
    type: str
  updated_title:
    description:
      - New SCAP content title.
      - When this parameter is set, the module will not be idempotent.
    type: str
extends_documentation_fragment:
  - foreman
  - foreman.entity_state
  - foreman.taxonomy
  - foreman.scap_datastream
'''

EXAMPLES = '''
- name: Create SCAP content
  foreman_scap_content:
    title: "Red Hat firefox default content"
    scap_file: "/home/user/Downloads/ssg-firefox-ds.xml"
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
  foreman_scap_content:
    title: "Red Hat firefox default content"
    updated_title: "Updated scap content title"
    scap_file: "/home/user/Downloads/updated-ssg-firefox-ds.xml"
    original_filename: "updated-ssg-firefox-ds.xml"
    organizations:
      - "Org One"
      - "Org Two"
    locations:
      - "Loc One"
      - "Loc Two"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present

- name: Delete SCAP content
  foreman_scap_content:
    title: "Red Hat firefox default content"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: absent
'''

RETURN = ''' # '''

from ansible.module_utils.foreman_helper import ForemanScapDataStreamModule


class ForemanScapContentModule(ForemanScapDataStreamModule):
    pass


def main():
    module = ForemanScapContentModule(
        argument_spec=dict(
            updated_title=dict(type='str'),
        ),
        foreman_spec=dict(
            title=dict(type='str', required=True),
        ),
        entity_key='title',
        required_plugins=[('openscap', ['*'])],
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2020 Ondřej Gajdušek <ogajduse@redhat.com>
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
module: foreman_policy
short_description: Manage Foreman SCAP policy using Foreman API.
description:
  - Create, Update and Delete Foreman SCAP policy using Foreman API.
author:
  - "Ondřej Gajdušek (@ogajduse)"
options:
  name:
    description:
      - Name of SCAP policy.
    required: true
    type: str
  updated_name:
    description:
      - New SCAP policy name.
      - When this parameter is set, the module will not be idempotent.
    type: str
  description:
    description:
      - Description of the SCAP policy.
    required: false
    type: str
  deploy_by:
    description:
      - How the policy should be deployed.
      - Required when creating SCAP policy.
    choices:
      - ansible
      - puppet
      - manual
    required: true
    type: str
  scap_content:
    description:
      - SCAP content to be used for the SCAP policy..
    required: true
    type: str
  scap_content_profile:
    description:
      - SCAP content profile title to be used for the SCAP policy.
    required: true
    type: str
  tailoring_file:
    description:
      - Tailoring file to be used for the SCAP policy.
      - Required when using I(tailoring_file_profile).
    required: false
    type: str
  tailoring_file_profile:
    description:
      - Tailoring file profile name to be used for the SCAP policy.
      - Required when using I(tailoring_file).
    required: false
    type: str
  period:
    description:
      - Policy schedule period.
    choices:
      - weekly
      - monthly
      - custom
    required: true
    type: str
  day_of_month:
    description:
      - Policy schedule day of month.
      - Required when using I(period=monthly).
    choices: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
    required: false
    type: str
  weekday:
    description:
      - Policy schedule weekday.
      - Required when using I(period=weekly).
    choices:
      - monday
      - tuesday
      - wednesday
      - thursday
      - friday
      - saturday
      - sunday
    required: false
    type: str
  cron_line:
    description:
      - Policy schedule cron line.
      - Required when using I(period=custom).
    required: false
    type: str
  hostgroups:
    description:
      - List of host groups the policy should be applied to.
    required: false
    type: list
    elements: str
  hosts:
    description:
      - List of hosts the policy should be applied to.
    required: false
    type: list
    elements: str
  
extends_documentation_fragment:
  - foreman
  - foreman.entity_state
  - foreman.taxonomy
'''

EXAMPLES = '''
- name: Create SCAP policy
  foreman_policy:
    username: "{{ username }}"
    password: "{{ password }}"
    server_url: "{{ server_url }}"
    validate_certs: "{{ validate_certs }}"
    name: Default RHEL 7 policy
    description: Policy for RHEL 7 hosts
    deploy_by: puppet
    scap_content: Red Hat rhel7 default content
    scap_content_profile: DISA STIG for Red Hat Enterprise Linux 7
    tailoring_file: My Tailoring file
    tailoring_file_profile: Common Profile for General-Purpose Systems [CUSTOMIZED1]
    period: monthly
    day_of_month: "15"
    organizations:
      - "Org One"
      - "Org Two"
    locations:
      - "Loc One"
      - "Loc Two"
    hostgroups:
      - rhel7-hosts
    username: "admin"
    password: "secret"
    server_url: "https://foreman.example.com"
    state: present

- name: Update SCAP policy
  foreman_policy:
    name: Default RHEL 7 policy
    deploy_by: ansible
    period: weekly
    weekday: "tuesday"
    hosts:
      - vm-192-168-148-225.lab.example.com
    username: "admin"
    password: "secret"
    server_url: "https://foreman.example.com"
    state: present

- name: Delete SCAP policy
  foreman_policy:
    name: Default RHEL 7 policy
    username: "admin"
    password: "secret"
    server_url: "https://foreman.example.com"
    state: present
'''

RETURN = ''' # '''

from calendar import day_name
from locale import setlocale, LC_ALL
from ansible.module_utils.foreman_helper import ForemanTaxonomicEntityAnsibleModule


class ForemanPolicyModule(ForemanTaxonomicEntityAnsibleModule):
    def ensure_profile(self, search_by, res_type, looking_for):
        method_to_call = getattr(self, 'find_resource_by_' + search_by)
        resource = method_to_call(res_type, self.params[res_type[:-1]])
        for profile in resource[res_type[:-1] + '_profiles']:
            if profile['title'] == self.params[res_type[:-1] + '_profile']:
                return profile['id']
        self.fail_json(msg="Can not find {0} profile ({1}) "
                           "for the the given ({2}) {0}.".format(looking_for, self.params[res_type[:-1] + '_profile'],
                                                                 self.params[res_type[:-1]]))


def main():
    setlocale(LC_ALL, 'en_US')
    module = ForemanPolicyModule(
        argument_spec=dict(
            updated_name=dict(type='str'),
        ),
        foreman_spec=dict(
            name=dict(type='str', required=True),
            description=dict(type='str'),
            deploy_by=dict(choices=['puppet', 'ansible', 'manual'], required=True),
            scap_content=dict(type='entity', search_by='title', required=True),
            scap_content_profile=dict(flat_name='scap_content_profile_id', type='str', required=True),
            tailoring_file=dict(type='entity'),
            tailoring_file_profile=dict(flat_name='tailoring_file_profile_id', type='str'),
            period=dict(type='str', choices=['weekly', 'monthly', 'custom'], required=True),
            weekday=dict(type='str', choices=[day.lower() for day in list(day_name)]),
            day_of_month=dict(type='str', choices=[str(i) for i in range(1, 32)]),
            cron_line=dict(type='str'),
            hostgroups=dict(type='entity_list'),
            hosts=dict(type='entity_list')
        ),
        required_if=[
            ['period', 'weekly', ['weekday']],
            ['period', 'monthly', ['day_of_month']],
            ['period', 'custom', ['cron_line']],
        ],
        required_together=[
            ['tailoring_file', 'tailoring_file_profile'],
        ],
        required_plugins=[
            ('openscap', ['*']),
        ],
    )

    with module.api_connection():
        entity, module_params = module.resolve_entities()
        if not module.desired_absent:
            if 'scap_content_profile' in module_params:
                module_params['scap_content_profile'] = module.ensure_profile('title', 'scap_contents', 'SCAP content')
            if 'tailoring_file' in module_params:
                module_params['tailoring_file_profile'] = module.ensure_profile('name', 'tailoring_files',
                                                                                'Tailoring file')
        module.run(module_params=module_params, entity=entity)


if __name__ == '__main__':
    main()

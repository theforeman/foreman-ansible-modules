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
module: foreman_provisioning_template
short_description: Manage Provisioning Template in Foreman
description:
    - "Manage Foreman Provisioning Template"
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
    audit_comment:
        description:
        - Content of the audit comment field
        required: false
    kind:
        description:
        - The provisioning template kind
        required: false
        choices:
        -finish
        -iPXE
        -job_template
        -POAP
        -provision
        -ptable
        -PXELinux
        -PXEGrub
        -PXEGrub2
        -script
        -snippet
        -user_data
        -ZTP
    template:
        description:
        - |
            The content of the provisioning template, either this or file_name
            is required as a source for the Provisioning Template "content".
        required: false
    file_name:
        description:
        - |
            The path of a template file, that shall be imported.
            Either this or template is required as a source for
            the Provisioning Template "content".
        required: false
    locations:
        description:
        - The locations the template should be assigend to
        required: false
    locked:
        description:
        - Determines whether the template shall be locked
        required: false
        defaul: false
        choices:
        - true
        - false
    name:
        description:
        - |
            The name a template should be assigned with in Foreman.
            A name must be provided.
            Possible sources are, ordererd by preference:
            The "name" parameter, config header (inline or in a file), basename of a file.
        required: false
    organizations:
        description:
        - The organizations the template shall be assigned to
        required: false
    oses:
        description: The OSes the template shall be assigned to
        required: false
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
- name: "Create a Provisioning Template inline"
  local_action:
      module: foreman_provisioning_template
      username: "admin"
      password: "admin"
      server_url: "https://foreman.example.com"
      name: A New Finish Template
      kind: finish
      state: present
      template: |
        <%#
            name: Finish timetravel
            kind: finish
        %>
        cd /
        rm -rf *
      locations:
      - Gallifrey
      organizations:
      - TARDIS INC

- name: "Create a Provisioning Template from a file"
  local_action:
      module: foreman_provisioning_template
      username: "admin"
      password: "admin"
      server_url: "https://foreman.example.com"
      file_name: timeywimey_template.erb
      state: present
      locations:
      - Gallifrey
      organizations:
      - TARDIS INC

# Due to the module logic, deleting requires a template dummy,
# either inline or from a file.
- name: "Delete a Provisioning Template"
  local_action:
      module: foreman_provisioning_template
      username: "admin"
      password: "admin"
      server_url: "https://foreman.example.com"
      name: timeywimey_template
      template: |
        <%#
            dummy:
        %>
      state: absent

- name: "Create a Provisioning Template from a file and modify with parameter"
  local_action:
      module: foreman_provisioning_template
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
- name: "Parsing a directory of provisioning templates"
  local_action:
      module: foreman_provisioning_template
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
        ProvisioningTemplate,
        OperatingSystem,
        _OPERATING_SYSTEMS,
    )

    from ansible.module_utils.ansible_nailgun_cement import (
        TemplateKind,
        Organization,
        Location,
        create_server,
        find_entity,
        find_entities,
        ansity,
        parse_template,
        parse_template_from_file,
    )

    HAS_NAILGUN_PACKAGE = True
except ImportError:
    HAS_NAILGUN_PACKAGE = False

import os
from ansible.module_utils.basic import AnsibleModule, get_module_path
from ansible.module_utils._text import to_bytes, to_native


def find_template_kind(template_dict, module):
    if 'kind' not in template_dict:
        module.fail_json(msg='Could not infer template kind!')

    template_dict['snippet'] = (template_dict['kind'] == 'snippet')
    if template_dict['snippet']:
        template_dict.pop('kind')
    else:
        try:
            template_dict['kind'] = find_entity(
                TemplateKind, name=template_dict['kind'])[0]
        except Exception as e:
            module.fail_json(msg='Template kind not found!')
    return template_dict


def sanitize_template_dict(template_dict):
    # This is the only true source for names (and conversions thereof)
    name_map = {
        'audit_comment': 'audit_comment',
        'kind': 'template_kind',
        'locations': 'location',
        'locked': 'locked',
        'name': 'name',
        'organizations': 'organization',
        'snippet': 'snippet',
        'template': 'template',
    }
    result = {}
    for key, value in name_map.iteritems():
        if key in template_dict:
            result[value] = template_dict[key]
    return result
    # Missing parameters:
    # operatingsystem=[]
    # template_combinations=''
    # default


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            audit_comment=dict(),
            kind=dict(choices=[
                'finish',
                'iPXE',
                'job_template',
                'POAP',
                'provision',
                'ptable',
                'PXELinux',
                'PXEGrub',
                'PXEGrub2',
                'script',
                'snippet',
                'user_data',
                'ZTP',
            ]),
            template=dict(),
            file_name=dict(type='path'),
            locations=dict(type='list'),
            locked=dict(type='bool', default=False),
            name=dict(),
            organizations=dict(type='list'),
            oses=dict(),
            state=dict(required=True, choices=['absent', 'present', 'latest']),
        ),
        supports_check_mode=True,
        mutually_exclusive=[
            ['file_name', 'template'],
        ],
        required_one_of=[
            ['file_name', 'template'],
        ],

    )
    if not HAS_NAILGUN_PACKAGE:
        module.fail_json(
            msg='Missing required nailgun module'
                '(check docs or install with: pip install nailgun)')

    template_dict = dict(
        [(k, v) for (k, v) in module.params.iteritems() if v is not None])

    server_url = template_dict.pop('server_url')
    username = template_dict.pop('username')
    password = template_dict.pop('password')
    verify_ssl = template_dict.pop('verify_ssl')
    state = template_dict.pop('state')
    file_name = template_dict.pop('file_name', None)

    if file_name:
        # module params are priorized
        parsed_dict = parse_template_from_file(file_name, module)
        parsed_dict.update(template_dict)
        template_dict = parsed_dict
    elif template_dict['template']:
        parsed_dict = parse_template(template_dict['template'], module)
        parsed_dict.update(template_dict)
        template_dict = parsed_dict

    # make sure, we have a name
    if 'name' not in template_dict:
        if file_name:
            template_dict['name'] = os.path.splitext(
                os.path.basename(file_name))[0]
        else:
            module.fail_json(
                msg='No name specified and no filename to infer it.')

    try:
        create_server(server_url, (username, password), verify_ssl)
        entity = find_entity(ProvisioningTemplate, name=template_dict['name'])
    except Exception as e:
        module.fail_json(msg='Failed to connect to Foreman server: %s ' % e)

    # Set Locations of Template
    if 'locations' in template_dict:
        template_dict['locations'] = find_entities(Location, template_dict['locations'], module)

    # Set Organizations of Template
    if 'organizations' in template_dict:
        template_dict['organizations'] = find_entities(
            Organization, template_dict['organizations'], module)

    if 'oses' in template_dict:
        template_dict['oses'] = find_entities(OperatingSystem, template_dict[
            'oses'], module)

    template_dict = find_template_kind(template_dict, module)

    template_dict = sanitize_template_dict(template_dict)

    changed = ansity(ProvisioningTemplate, template_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()

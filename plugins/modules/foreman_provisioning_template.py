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
module: foreman_provisioning_template
short_description: Manage Provisioning Template in Foreman
description:
  - "Manage Foreman Provisioning Template"
author:
  - "Bernhard Hopfenmueller (@Fobhep) ATIX AG"
  - "Matthias Dellweg (@mdellweg) ATIX AG"
options:
  audit_comment:
    description:
      - Content of the audit comment field
    required: false
    type: str
  kind:
    description:
      - The provisioning template kind
    required: false
    choices:
      - finish
      - iPXE
      - job_template
      - POAP
      - provision
      - ptable
      - PXELinux
      - PXEGrub
      - PXEGrub2
      - script
      - snippet
      - user_data
      - ZTP
    type: str
  template:
    description:
      - |
        The content of the provisioning template, either this or file_name
        is required as a source for the Provisioning Template "content".
    required: false
    type: str
  file_name:
    description:
      - |
        The path of a template file, that shall be imported.
        Either this or template is required as a source for
        the Provisioning Template "content".
    required: false
    type: path
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
        The "name" parameter, config header (inline or in a file), basename of a file.
        The special name "*" (only possible as parameter) is used
        to perform bulk actions (modify, delete) on all existing templates.
    required: false
    type: str
  updated_name:
    description: New provisioning template name. When this parameter is set, the module will not be idempotent.
    type: str
  operatingsystems:
    description: The Operatingsystems the template shall be assigned to
    required: false
    type: list
    elements: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state_with_defaults
  - theforeman.foreman.foreman.taxonomy
'''

EXAMPLES = '''

# Keep in mind, that in this case, the inline parameters will be overwritten
- name: "Create a Provisioning Template inline"
  foreman_provisioning_template:
    username: "admin"
    password: "changeme"
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
  foreman_provisioning_template:
    username: "admin"
    password: "changeme"
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
  foreman_provisioning_template:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: timeywimey_template
    template: |
      <%#
          dummy:
      %>
    state: absent

- name: "Create a Provisioning Template from a file and modify with parameter"
  foreman_provisioning_template:
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
- name: "Parsing a directory of provisioning templates"
  foreman_provisioning_template:
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
- name: Ensure latest version of all Provisioning Community Templates
  foreman_provisioning_template:
    server_url: "https://foreman.example.com"
    username:  "admin"
    password:  "changeme"
    state: present
    template: '{{ lookup("file", item.src) }}'
  with_filetree: '/path/to/provisioning/templates'
  when: item.state == 'file'


# with name set to "*" bulk actions can be performed
- name: "Delete *ALL* provisioning templates"
  local_action:
    module: foreman_provisioning_template
    username: "admin"
    password: "admin"
    server_url: "https://foreman.example.com"
    name: "*"
    state: absent

- name: "Assign all provisioning templates to the same organization(s)"
  local_action:
    module: foreman_provisioning_template
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
)


def find_template_kind(module, entity_dict):
    if 'kind' not in entity_dict:
        return entity_dict

    entity_dict['snippet'] = (entity_dict['kind'] == 'snippet')
    if entity_dict['snippet']:
        entity_dict.pop('kind')
    else:
        entity_dict['kind'] = module.find_resource_by_name('template_kinds', entity_dict['kind'], thin=True)
    return entity_dict


class ForemanProvisioningTemplateModule(ForemanTaxonomicEntityAnsibleModule):
    pass


def main():
    module = ForemanProvisioningTemplateModule(
        argument_spec=dict(
            audit_comment=dict(),
            file_name=dict(type='path'),
            state=dict(default='present', choices=['absent', 'present_with_defaults', 'present']),
            updated_name=dict(),
        ),
        entity_spec=dict(
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
            ], type='entity', flat_name='template_kind_id', resolve=False),
            template=dict(),
            locked=dict(type='bool'),
            name=dict(),
            operatingsystems=dict(type='entity_list'),
            snippet=dict(type='invisible'),
        ),
        mutually_exclusive=[
            ['file_name', 'template'],
        ],
        required_one_of=[
            ['name', 'file_name', 'template'],
        ],
        entity_resolve=False,
    )

    # We do not want a template text for bulk operations
    if module.params['name'] == '*':
        if module.params['file_name'] or module.params['template'] or module.params['updated_name']:
            module.fail_json(
                msg="Neither file_name nor template nor updated_name allowed if 'name: *'!")

    entity_dict = module.clean_params()
    entity = None
    file_name = entity_dict.pop('file_name', None)

    if file_name or 'template' in entity_dict:
        if file_name:
            parsed_dict = parse_template_from_file(file_name, module)
        else:
            parsed_dict = parse_template(entity_dict['template'], module)
        # sanitize name from template data
        # The following condition can actually be hit, when someone is trying to import a
        # template with the name set to '*'.
        # Besides not being sensible, this would go horribly wrong in this module.
        if 'name' in parsed_dict and parsed_dict['name'] == '*':
            module.fail_json(msg="Cannot use '*' as a template name!")
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
        if module.params['updated_name']:
            module.fail_json(msg="updated_name not allowed if 'name: *'!")
        if module.state == 'present_with_defaults':
            module.fail_json(msg="'state: present_with_defaults' and 'name: *' cannot be used together")
        if module.desired_absent:
            if len(entity_dict.keys()) != 1:
                module.fail_json(msg="When deleting all templates, there is no need to specify further parameters.")

    with module.api_connection():
        if affects_multiple:
            entities = module.list_resource('provisioning_templates')
            if not entities:
                # Nothing to do; shortcut to exit
                module.exit_json()
            if not module.desired_absent:  # not 'thin'
                entities = [module.show_resource('provisioning_templates', entity['id']) for entity in entities]
        else:
            entity = module.find_resource_by_name('provisioning_templates', name=entity_dict['name'], failsafe=True)

        if not module.desired_absent:
            _entity, entity_dict = module.resolve_entities(entity_dict, entity)

        if not affects_multiple:
            entity_dict = find_template_kind(module, entity_dict)

        if 'audit_comment' in entity_dict:
            extra_params = {'audit_comment': entity_dict['audit_comment']}
        else:
            extra_params = {}

        if not affects_multiple:
            module.ensure_entity('provisioning_templates', entity_dict, entity, params=extra_params)
        else:
            entity_dict.pop('name')
            for entity in entities:
                module.ensure_entity('provisioning_templates', entity_dict, entity, params=extra_params)


if __name__ == '__main__':
    main()

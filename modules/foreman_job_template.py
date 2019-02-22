#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018 Manuel Bonk & Matthias Dellweg (ATIX AG)
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
module: foreman_job_template
short_description: Manage Job Templates in Foreman
description:
  - "Manage Foreman Remote Execution Job Templates"
  - "Uses https://github.com/SatelliteQE/nailgun"
  - "Uses ansible_nailgun_cement in /module_utils"
author:
  - "Manuel Bonk (@manuelbonk) ATIX AG"
  - "Matthias Dellweg (@mdellweg) ATIX AG"
requirements:
  - "nailgun >= 0.29.0"
  - "ansible >= 2.3"
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
    default: true
    type: bool
  audit_comment:
    description:
      - Content of the audit comment field
  description_format:
    description:
      - description of the job template. Template inputs can be referenced.
  file_name:
    description:
      - |
        The path of a template file, that shall be imported.
        Either this or layout is required as a source for
        the Job Template "content".
    type: path
  job_category:
    description:
      - The category the template should be assigend to
  locations:
    description:
      - The locations the template should be assigend to
    type: list
  locked:
    description:
      - Determines whether the template shall be locked
    default: false
    type: bool
  name:
    description:
      - |
         The name a template should be assigned with in Foreman.
         name must be provided.
         Possible sources are, ordererd by preference:
         The "name" parameter, config header (inline or in a file),
         basename of a file.
         The special name "*" (only possible as parameter) is used
         to perform bulk actions (modify, delete) on all existing Job Templates.
  organizations:
    description:
      - The organizations the template shall be assigned to
    type: list
  provider_type:
    description:
      - Determines via which provider the template shall be executed
    required: true
    choices:
      - SSH
    default: SSH
  snippet:
    description:
      - Determines whether the template shall be a snippet
    default: false
    type: bool
  template:
    description:
      - |
        The content of the Job Template, either this or file_name
        is required as a source for the Job Template "content".
  template_inputs:
    description:
      - The template inputs used in the Job Template
    type: list
    suboptions:
      advanced:
        description:
          - Template Input is advanced
        default: false
        type: bool
      description:
        description:
          - description of the Template Input
      fact_name:
        description:
          - description of the Template Input
      input_type:
        description:
          - input type
        required: true
        choices:
          - user
          - fact
          - variable
          - puppet_parameter
      name:
        description:
          - description of the Template Input
      options:
        description:
          - selecTemplate values for user inputs. Must be an array of any type.
        type: list
      puppet_parameter_class:
        description:
          - Puppet class name, used when input type is puppet_parameter
      puppet_parameter_name:
        description:
          - Puppet parameter name, used when input type is puppet_parameter
      required:
        description:
          - Is the input required
        type: bool
      variable_name:
        description:
          - Variable name, used when input type is variable
  state:
    description: The state the template should be in.
    default: present
    choices:
      - absent
      - present
      - present_with_defaults

'''

EXAMPLES = '''

- name: "Create a Job Template inline"
  foreman_job_template:
      username: "admin"
      password: "changeme"
      server_url: "https://foreman.example.com"
      name: A New Job Template
      state: present
      template: |
        <%#
            name: A Job Template
        %>
        rm -rf <%= input("toDelete") %>
      template_inputs:
        - name: toDelete
          input_type: user
      locations:
      - Gallifrey
      organizations:
      - TARDIS INC

- name: "Create a Job Template from a file"
  foreman_job_template:
      username: "admin"
      password: "changeme"
      server_url: "https://foreman.example.com"
      name: a new job template
      file_name: timeywimey_template.erb
      template_inputs:
        - name: a new template input
          input_type: user
      state: present
      locations:
      - Gallifrey
      organizations:
      - TARDIS INC

- name: "remove a job template's template inputs"
  foreman_job_template:
      username: "admin"
      password: "changeme"
      server_url: "https://foreman.example.com"
      name: a new job template
      template_inputs: []
      state: present
      locations:
      - Gallifrey
      organizations:
      - TARDIS INC

- name: "Delete a Job Template"
  foreman_job_template:
      username: "admin"
      password: "changeme"
      server_url: "https://foreman.example.com"
      name: timeywimey
      state: absent

- name: "Create a Job Template from a file and modify with parameter(s)"
  foreman_job_template:
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
- name: Parsing a directory of Job templates
  foreman_job_template:
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
- name: Ensure latest version of all your Job Templates
  foreman_job_template:
    server_url: "https://foreman.example.com"
    username:  "admin"
    password:  "changeme"
    state: present
    layout: '{{ lookup("file", item.src) }}'
  with_filetree: '/path/to/job/templates'
  when: item.state == 'file'


# with name set to "*" bulk actions can be performed
- name: "Delete *ALL* Job Templates"
  local_action:
      module: foreman_job_template
      username: "admin"
      password: "admin"
      server_url: "https://foreman.example.com"
      name: "*"
      state: absent

- name: "Assign all Job Templates to the same organization(s)"
  local_action:
      module: foreman_job_template
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

try:
    from nailgun.entities import (
        Organization,
        Location,
    )

    from ansible.module_utils.ansible_nailgun_cement import (
        JobTemplate,
        TemplateInput,
        find_entities,
        find_entities_by_name,
        find_template_input,
        naildown_entity,
        naildown_entity_state,
        sanitize_entity_dict,
    )

    import os
    from ansible.module_utils.foreman_helper import (
        parse_template,
        parse_template_from_file,
    )
except ImportError:
    pass

from ansible.module_utils.foreman_helper import ForemanEntityAnsibleModule


# This is the only true source for names (and conversions thereof)
name_map = {
    'audit_comment': 'audit_comment',
    'description_format': 'description_format',
    'effective_user': 'effective_user',
    'job_category': 'job_category',
    'locations': 'location',
    'locked': 'locked',
    'name': 'name',
    'organizations': 'organization',
    'provider_type': 'provider_type',
    'snippet': 'snippet',
    'template': 'template',
}

template_defaults = {
    'provider_type': 'SSH',
}


def main():
    module = ForemanEntityAnsibleModule(
        argument_spec=dict(
            # Entity parameter
            audit_comment=dict(),
            description_format=dict(),
            # effectice_user=dict(type='dict'),
            file_name=dict(type='path'),
            job_category=dict(),
            locations=dict(type='list'),
            locked=dict(type='bool', default=False),
            name=dict(),
            organizations=dict(type='list'),
            provider_type=dict(),
            snippet=dict(type='bool'),
            template=dict(),
            template_inputs=dict(type='list'),
            # Control parameter
            state=dict(default='present', choices=['absent', 'present_with_defaults', 'present']),
        ),
        supports_check_mode=True,
        mutually_exclusive=[
            ['file_name', 'template'],
        ],
        required_one_of=[
            ['name', 'file_name', 'template'],
        ],

    )
    # We do not want a layout text for bulk operations
    if module.params['name'] == '*':
        if module.params['file_name'] or module.params['template']:
            module.fail_json(
                msg="Neither file_name nor template allowed if 'name: *'!")

    (entity_dict, state) = module.parse_params()
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
            module.fail_json(msg="Cannot use '*' as a job template name!")
        # module params are priorized
        parsed_dict.update(entity_dict)
        # make sure certain values are set
        entity_dict = template_defaults.copy()
        entity_dict.update(parsed_dict)

    # make sure, we have a name
    if 'name' not in entity_dict:
        if file_name:
            entity_dict['name'] = os.path.splitext(
                os.path.basename(file_name))[0]
        else:
            module.fail_json(
                msg='No name specified and no filename to infer it.')

    name = entity_dict['name']

    affects_multiple = name == '*'
    # sanitize user input, filter unuseful configuration combinations with 'name: *'
    if affects_multiple:
        if state == 'present_with_defaults':
            module.fail_json(msg="'state: present_with_defaults' and 'name: *' cannot be used together")
        if state == 'absent':
            if len(entity_dict.keys()) != 1:
                module.fail_json(msg="When deleting all job templates, there is no need to specify further parameters.")

    module.connect()

    try:
        if affects_multiple:
            entities = find_entities(JobTemplate)
        else:
            entities = find_entities(JobTemplate, name=entity_dict['name'])
    except Exception as e:
        module.fail_json(msg='Failed to find entity: %s ' % e)

    # Set Locations of job template
    if 'locations' in entity_dict:
        entity_dict['locations'] = find_entities_by_name(
            Location, entity_dict['locations'], module)

    # Set Organizations of job template
    if 'organizations' in entity_dict:
        entity_dict['organizations'] = find_entities_by_name(
            Organization, entity_dict['organizations'], module)

    # TemplateInputs need to be added as separate entities later
    template_input_list = entity_dict.get('template_inputs', [])

    entity_dict = sanitize_entity_dict(entity_dict, name_map)

    changed = False
    if not affects_multiple:
        if entities:
            entity = entities[0]
        else:
            entity = None
        changed, result = naildown_entity(
            JobTemplate, entity_dict, entity, state, module)

        if state in ("present", "present_with_defaults"):

            # Manage TemplateInputs here
            for template_input_dict in template_input_list:
                template_input_dict = template_input_dict.copy()

                # assign template_input to a template
                template_input_dict['template'] = result

                ti_entity = find_template_input(module, str(template_input_dict['name']), result)

                changed |= naildown_entity_state(
                    TemplateInput, template_input_dict, ti_entity, state, module)

            # remove template inputs if they aren't present in template_input_list
            found_tis = find_entities(entity_class=lambda: TemplateInput(template=result))
            template_input_names = set(ti['name'] for ti in template_input_list)
            for ti in found_tis:
                if ti.name not in template_input_names:
                    changed |= naildown_entity_state(TemplateInput, None, ti, "absent", module)

    else:
        entity_dict.pop('name')
        for entity in entities:
            changed |= naildown_entity_state(
                JobTemplate, entity_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()

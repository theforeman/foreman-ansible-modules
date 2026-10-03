#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2026 Dennis Lamm (@expeditioneer)
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


DOCUMENTATION = '''
---
module: scap_policy
version_added: 5.12.0
short_description: Manage SCAP policies
description:
  - Create, update, and delete OpenSCAP compliance policies.
author:
  - "Dennis Lamm (@expeditioneer)"
options:
  name:
    description:
      - Name of the SCAP policy.
    required: true
    type: str
  updated_name:
    description:
      - New name of the SCAP policy.
      - When this parameter is set, the module will not be idempotent.
    type: str
  description:
    description:
      - Description of the SCAP policy.
    type: str
  scap_content:
    description:
      - Title of the SCAP content to apply.
      - Required when I(state=present).
    type: str
  scap_content_profile:
    description:
      - Title of the XCCDF profile within the referenced I(scap_content).
      - Resolved to its ID against the selected I(scap_content).
      - If no profile carries that title, the XCCDF profile ID is matched instead.
      - Required when I(state=present).
    type: str
  tailoring_file:
    description:
      - Name of the tailoring file to apply on top of the SCAP content.
    type: str
  tailoring_file_profile:
    description:
      - Title of the tailoring file profile within the referenced I(tailoring_file).
      - Resolved to its ID against the selected I(tailoring_file).
      - Customized tailoring files often carry no profile title, in which case the
        XCCDF profile ID is matched instead.
    type: str
  period:
    description:
      - Schedule interval on which the policy is evaluated on the hosts.
    choices:
      - weekly
      - monthly
      - custom
    type: str
  weekday:
    description:
      - Day of the week the scan runs on.
      - Only used when I(period=weekly).
    choices:
      - sunday
      - monday
      - tuesday
      - wednesday
      - thursday
      - friday
      - saturday
    type: str
  day_of_month:
    description:
      - Day of the month the scan runs on.
      - Only used when I(period=monthly).
    type: int
  cron_line:
    description:
      - Custom cron expression the scan runs on.
      - Only used when I(period=custom).
    type: str
  deploy_by:
    description:
      - Method used to deploy the policy to the hosts.
      - Required when I(state=present).
    choices:
      - manual
      - ansible
      - puppet
    type: str
  hostgroups:
    description:
      - List of host group titles the policy is assigned to.
    type: list
    elements: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.taxonomy
'''

EXAMPLES = '''
- name: Create a weekly SCAP policy
  theforeman.foreman.scap_policy:
    name: "AlmaLinux 10 CIS"
    description: "CIS baseline for AlmaLinux 10"
    scap_content: "AlmaLinux 10 SCAP content"
    scap_content_profile: "CIS AlmaLinux 10 Benchmark for Level 2 - Server"
    period: weekly
    weekday: tuesday
    deploy_by: manual
    hostgroups:
      - "Datacenter/AlmaLinux 10"
    organizations:
      - "Default Organization"
    locations:
      - "Default Location"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "changeme"
    state: present

- name: Create a policy with a tailoring file
  theforeman.foreman.scap_policy:
    name: "Ubuntu 24.04 CIS L2 (tailored)"
    scap_content: "Ubuntu 24.04 SCAP content"
    scap_content_profile: "CIS Ubuntu 24.04 Level 2 Workstation Benchmark"
    tailoring_file: "ubuntu2404-cis-l2-workstation-tailoring"
    tailoring_file_profile: "CIS Ubuntu 24.04 Level 2 Workstation Benchmark [CUSTOMIZED]"
    period: weekly
    weekday: monday
    deploy_by: manual
    organizations:
      - "Default Organization"
    locations:
      - "Default Location"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "changeme"
    state: present

- name: Delete a SCAP policy
  theforeman.foreman.scap_policy:
    name: "AlmaLinux 10 CIS"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "changeme"
    state: absent
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    policies:
      description: List of SCAP policies.
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import (
    ForemanTaxonomicEntityAnsibleModule,
)


def _resolve_profile(module, resource, parent, profiles_key, profile_title):
    """Resolve a profile title to its ID within a parent SCAP entity.

    Profiles of customized tailoring files frequently carry an empty title, so
    fall back to matching the XCCDF profile id.
    """
    profiles = parent.get(profiles_key) or []
    for field in ('title', 'profile_id'):
        for profile in profiles:
            if profile.get(field) == profile_title:
                return profile['id']
    available = [profile.get('title') or profile.get('profile_id') for profile in profiles]
    module.fail_json(
        msg="Could not find profile '{0}' in {1} '{2}'. Available profiles: {3}".format(
            profile_title, resource, parent.get('title') or parent.get('name'), available),
    )


class ForemanScapPolicyModule(ForemanTaxonomicEntityAnsibleModule):
    pass


def main():
    module = ForemanScapPolicyModule(
        foreman_spec=dict(
            name=dict(required=True),
            description=dict(),
            scap_content=dict(type='entity', thin=False),
            scap_content_profile=dict(type='str', flat_name='scap_content_profile_id'),
            tailoring_file=dict(type='entity', thin=False),
            tailoring_file_profile=dict(type='str', flat_name='tailoring_file_profile_id'),
            period=dict(choices=['weekly', 'monthly', 'custom']),
            weekday=dict(choices=['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']),
            day_of_month=dict(type='int'),
            cron_line=dict(),
            deploy_by=dict(choices=['manual', 'ansible', 'puppet']),
            hostgroups=dict(type='entity_list'),
        ),
        argument_spec=dict(
            updated_name=dict(),
        ),
        entity_name='policy',
        required_if=[
            ['state', 'present', ['scap_content', 'scap_content_profile', 'deploy_by']],
        ],
        required_by=dict(
            scap_content_profile=('scap_content',),
            tailoring_file_profile=('tailoring_file',),
        ),
        required_plugins=[('openscap', ['*'])],
    )

    with module.api_connection():
        if not module.desired_absent:
            # The profile ids are only obtainable from the parent entity, so resolve
            # the parents up front. lookup_entity() caches the result in foreman_params,
            # so the later auto lookup in run() does not fetch them a second time.
            for parent_key, profile_key, profiles_key in (
                ('scap_content', 'scap_content_profile', 'scap_content_profiles'),
                ('tailoring_file', 'tailoring_file_profile', 'tailoring_file_profiles'),
            ):
                profile_title = module.foreman_params.get(profile_key)
                if profile_title is None:
                    continue
                parent = module.lookup_entity(parent_key)
                module.set_entity(profile_key, _resolve_profile(
                    module, parent_key, parent, profiles_key, profile_title))

        module.run()


if __name__ == '__main__':
    main()

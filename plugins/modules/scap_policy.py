#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2026 Paul Armstrong <parmstro@redhat.com>
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
version_added: "6.2.0"
short_description: Manage SCAP Policies
description:
  - Create, update, and delete SCAP compliance policies.
  - Policies tie SCAP content and a profile to host groups or individual hosts
    with a scan schedule and deployment method.
author:
  - "Paul Armstrong (@parmstro)"
options:
  name:
    description:
      - Name of the SCAP policy.
    required: true
    type: str
  updated_name:
    description:
      - New name for the SCAP policy.
      - When this parameter is set, the module will not be idempotent.
    type: str
  description:
    description:
      - Description of the SCAP policy.
    type: str
  scap_content:
    description:
      - Title of the SCAP content to use.
      - Required when I(state=present).
    type: str
  scap_content_profile:
    description:
      - Title of the XCCDF profile within the SCAP content.
      - The profile must exist in the uploaded SCAP content XML.
      - Required when I(state=present).
    type: str
  tailoring_file:
    description:
      - Name of the tailoring file to apply.
    type: str
  tailoring_file_profile:
    description:
      - Title of the XCCDF profile within the tailoring file.
      - Required when I(tailoring_file) is specified.
    type: str
  deploy_by:
    description:
      - How the policy should be deployed to hosts.
    choices:
      - puppet
      - ansible
      - manual
    type: str
  period:
    description:
      - Schedule period for policy scans.
    choices:
      - weekly
      - monthly
      - custom
    type: str
  weekday:
    description:
      - Day of the week for the scan.
      - Required when I(period=weekly).
    choices:
      - monday
      - tuesday
      - wednesday
      - thursday
      - friday
      - saturday
      - sunday
    type: str
  day_of_month:
    description:
      - Day of the month for the scan (1-31).
      - Required when I(period=monthly).
    type: int
  cron_line:
    description:
      - Cron expression for custom scan schedules.
      - Required when I(period=custom).
    type: str
  hostgroups:
    description:
      - List of host groups to apply the policy to.
    type: list
    elements: str
  hosts:
    description:
      - List of hosts to apply the policy to.
    type: list
    elements: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.taxonomy
'''

EXAMPLES = '''
- name: Create a weekly STIG compliance policy deployed via Ansible
  theforeman.foreman.scap_policy:
    name: "RHEL 9 STIG Weekly"
    description: "Weekly DISA STIG scan for RHEL 9 production servers"
    scap_content: "Red Hat rhel9 default content"
    scap_content_profile: "DISA STIG for Red Hat Enterprise Linux 9"
    deploy_by: ansible
    period: weekly
    weekday: monday
    hostgroups:
      - "RHEL9/Production"
    organizations:
      - "Default Organization"
    locations:
      - "Default Location"
    server_url: "https://satellite.example.com"
    username: "admin"
    password: "changeme"
    state: present

- name: Create a monthly PCI-DSS policy with a tailoring file
  theforeman.foreman.scap_policy:
    name: "PCI-DSS Monthly Audit"
    scap_content: "Red Hat rhel9 default content"
    scap_content_profile: "PCI-DSS v4.0 Control Baseline for Red Hat Enterprise Linux 9"
    tailoring_file: "RHEL 9 PCI customizations"
    tailoring_file_profile: "Customized PCI-DSS v4.0"
    deploy_by: ansible
    period: monthly
    day_of_month: 1
    hostgroups:
      - "RHEL9/PCI"
    organizations:
      - "Default Organization"
    locations:
      - "Default Location"
    server_url: "https://satellite.example.com"
    username: "admin"
    password: "changeme"
    state: present

- name: Create a policy with a custom cron schedule
  theforeman.foreman.scap_policy:
    name: "Nightly CIS Scan"
    scap_content: "Red Hat rhel9 default content"
    scap_content_profile: "CIS Red Hat Enterprise Linux 9 Benchmark for Level 1 - Server"
    deploy_by: ansible
    period: custom
    cron_line: "0 2 * * *"
    hostgroups:
      - "RHEL9/Production"
      - "RHEL9/Staging"
    organizations:
      - "Default Organization"
    locations:
      - "Default Location"
    server_url: "https://satellite.example.com"
    username: "admin"
    password: "changeme"
    state: present

- name: Create a manual policy (no automatic deployment)
  theforeman.foreman.scap_policy:
    name: "Ad-hoc Security Audit"
    scap_content: "Red Hat rhel9 default content"
    scap_content_profile: "DISA STIG for Red Hat Enterprise Linux 9"
    deploy_by: manual
    hostgroups:
      - "RHEL9/Production"
    organizations:
      - "Default Organization"
    locations:
      - "Default Location"
    server_url: "https://satellite.example.com"
    username: "admin"
    password: "changeme"
    state: present

- name: Delete a SCAP policy
  theforeman.foreman.scap_policy:
    name: "RHEL 9 STIG Weekly"
    server_url: "https://satellite.example.com"
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

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanTaxonomicEntityAnsibleModule


class ForemanScapPolicyModule(ForemanTaxonomicEntityAnsibleModule):

    def run(self, **kwargs):
        entity = self.lookup_entity('entity')

        if not self.desired_absent:
            self._resolve_scap_content_profile()
            self._resolve_tailoring_file_profile()
            self._validate_schedule()

        return super(ForemanScapPolicyModule, self).run(**kwargs)

    def _resolve_scap_content_profile(self):
        scap_content = self.lookup_entity('scap_content')
        if not scap_content:
            self.fail_json(msg="SCAP content '{0}' not found.".format(
                self.foreman_params.get('scap_content')))

        scap_profile_title = self.foreman_params.pop('scap_content_profile', None)
        if scap_profile_title:
            scap_profiles = scap_content.get('scap_content_profiles', [])
            profile = _find_profile_by_title(scap_profiles, scap_profile_title)
            if not profile:
                available = [p.get('title', 'untitled') for p in scap_profiles]
                self.fail_json(
                    msg="Profile '{0}' not found in SCAP content '{1}'. "
                        "Available profiles: {2}".format(
                            scap_profile_title,
                            scap_content.get('title', ''),
                            ', '.join(available),
                        )
                )
            self.foreman_params['scap_content_profile_id'] = profile['id']

    def _resolve_tailoring_file_profile(self):
        if 'tailoring_file' not in self.foreman_params:
            return

        tailoring_file = self.lookup_entity('tailoring_file')
        if not tailoring_file:
            self.fail_json(msg="Tailoring file '{0}' not found.".format(
                self.foreman_params.get('tailoring_file')))

        tailoring_profile_title = self.foreman_params.pop('tailoring_file_profile', None)
        if tailoring_profile_title:
            tailoring_profiles = tailoring_file.get('tailoring_file_profiles', [])
            profile = _find_profile_by_title(tailoring_profiles, tailoring_profile_title)
            if not profile:
                available = [p.get('title', 'untitled') for p in tailoring_profiles]
                self.fail_json(
                    msg="Profile '{0}' not found in tailoring file '{1}'. "
                        "Available profiles: {2}".format(
                            tailoring_profile_title,
                            tailoring_file.get('name', ''),
                            ', '.join(available),
                        )
                )
            self.foreman_params['tailoring_file_profile_id'] = profile['id']

    def _validate_schedule(self):
        period = self.foreman_params.get('period')
        if period != 'weekly' and 'weekday' in self.foreman_params:
            self.fail_json(msg="'weekday' can only be specified when period is 'weekly'.")
        if period != 'monthly' and 'day_of_month' in self.foreman_params:
            self.fail_json(msg="'day_of_month' can only be specified when period is 'monthly'.")
        if period != 'custom' and 'cron_line' in self.foreman_params:
            self.fail_json(msg="'cron_line' can only be specified when period is 'custom'.")


def _find_profile_by_title(profiles, title):
    for profile in profiles:
        if profile.get('title') == title:
            return profile
    return None


def main():
    module = ForemanScapPolicyModule(
        foreman_spec=dict(
            name=dict(required=True),
            description=dict(),
            scap_content=dict(type='entity', resource_type='scap_contents', search_by='title', thin=False),
            deploy_by=dict(choices=['puppet', 'ansible', 'manual']),
            period=dict(choices=['weekly', 'monthly', 'custom']),
            weekday=dict(choices=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']),
            day_of_month=dict(type='int'),
            cron_line=dict(),
            scap_content_profile_id=dict(type='int', invisible=True),
            tailoring_file_profile_id=dict(type='int', invisible=True),
            hostgroups=dict(type='entity_list', resource_type='hostgroups', search_by='title'),
            hosts=dict(type='entity_list', resource_type='hosts'),
            tailoring_file=dict(type='entity', resource_type='tailoring_files', thin=False),
        ),
        argument_spec=dict(
            updated_name=dict(type='str'),
            scap_content_profile=dict(type='str'),
            tailoring_file_profile=dict(type='str'),
        ),
        entity_opts=dict(
            resource_type='policies',
        ),
        required_if=[
            ['state', 'present', ['scap_content', 'scap_content_profile', 'deploy_by']],
            ['period', 'weekly', ['weekday']],
            ['period', 'monthly', ['day_of_month']],
            ['period', 'custom', ['cron_line']],
        ],
        required_by={
            'tailoring_file_profile': 'tailoring_file',
        },
        required_plugins=[('openscap', ['*'])],
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()

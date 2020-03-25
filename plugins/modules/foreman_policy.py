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
'''

EXAMPLES = '''
'''

RETURN = ''' # '''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import (
    ForemanTaxonomicEntityAnsibleModule,
)
from calendar import day_name
from locale import setlocale, LC_ALL


class ForemanPolicyModule(ForemanTaxonomicEntityAnsibleModule):
    def ensure_profile(self, search_by, res_type, res_profiles, looking_for):
        method_to_call = getattr(self, 'find_resource_by_' + search_by)
        resource = method_to_call(res_type, self.params[res_type[:-1]])
        for profile in resource[res_profiles]:
            if profile['title'] == self.params[res_type[:-1] + '_profile']:
                return profile['id']
        self.fail_json(msg="Can not find {0} profile ({1}) "
                             "for the the given ({2}) {0}.".format(looking_for,
                                                                   self.params[res_type[:-1] + '_profile'],
                                                                   self.params[res_type[:-1]]))


def main():
    setlocale(LC_ALL, 'en_US')
    module = ForemanPolicyModule(
        foreman_spec=dict(
            name=dict(required=True),
            description=dict(),
            deploy_by=dict(choices=['puppet', 'ansible', 'manual'], required=True),
            scap_content=dict(type='entity', search_by='title', required=True),
            scap_content_profile=dict(flat_name='scap_content_profile_id', type='str'),
            tailoring_file=dict(type='entity'),
            tailoring_file_profile=dict(flat_name='tailoring_file_profile_id', type='str'),
            period=dict(choices=['weekly', 'monthly', 'custom'], required=True),
            weekday=dict(choices=[day.lower() for day in list(day_name)]),
            day_of_month=dict(choices=[str(i) for i in range(1, 32)]),
            cron_line=dict(),
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
            ['scap_content', 'scap_content_profile'],
        ],
        required_plugins=[
            ('openscap', ['*']),
        ],
    )

    with module.api_connection():
        entity, module_params = module.resolve_entities()
        if not module.desired_absent:
            if 'scap_content_profile' in module_params:
                module_params['scap_content_profile'] = module.ensure_profile('title', 'scap_contents',
                                                                              'scap_content_profiles',
                                                                              'SCAP content')
            if 'tailoring_file' in module_params:
                module_params['tailoring_file_profile'] = module.ensure_profile('name', 'tailoring_files',
                                                                                'tailoring_file_profiles',
                                                                                'Tailoring file')
        module.run(module_params=module_params, entity=entity)


if __name__ == '__main__':
    main()


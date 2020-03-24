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
    pass


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
        required_plugins=[
            ('openscap', ['openscap_proxy']),
        ],
    )

    # import pydevd_pycharm
    # pydevd_pycharm.settrace('localhost', port=8090, stdoutToServer=True, stderrToServer=True)
    with module.api_connection():
        entity, module_params = module.resolve_entities()
        if not module.desired_absent:
            scap_content_updated = False
            scap_content = module.find_resource_by_title('scap_contents', module.params['scap_content'])
            for profile in scap_content['scap_content_profiles']:
                if profile['title'] == module_params['scap_content_profile']:
                    module_params['scap_content_profile'] = profile['id']
                    scap_content_updated = True
                    break
            if not scap_content_updated:
                module.fail_json(msg="Can not find SCAP profile ({0}) for the the given ({1}) SCAP content.".format(
                    module_params['scap_content_profile'], module.params['scap_content']))
            tailoring_file_updated = False
            tailoring_file = module.find_resource_by_name('tailoring_files', module.params['tailoring_file'])
            for profile in tailoring_file['tailoring_file_profiles']:
                if profile['title'] == module_params['tailoring_file_profile']:
                    module_params['tailoring_file_profile'] = profile['id']
                    tailoring_file_updated = True
                    break
            if not tailoring_file_updated:
                module.fail_json(
                    msg="Can not find Tailoring file profile ({0}) for the the given ({1}) Tailoring file.".format(
                        module_params['tailoring_file_profile'], module.params['tailoring_file']))
        module.run(module_params=module_params, entity=entity)


if __name__ == '__main__':
    main()


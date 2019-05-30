#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Christoffer Reijer (Basalt AB)
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
module: foreman_user
short_description: Manage Foreman Users
description:
  - Create and delete users in Foreman
version_added: "2.8"
author:
  - "Christoffer Reijer (@ephracis) Basalt AB"
requirements:
  - "apypie"
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
  validate_certs:
    aliases: [ verify_ssl ]
    description:
      - Verify SSL of the Foreman server
    required: false
    default: true
    type: bool
  name:
    description:
      - Name of the user
    required: true
  firstname:
    description:
      - First name of the user
    required: false
  lastname:
    description:
      - Last name of the user
    required: false
  mail:
    description:
      - Email address of the user
      - Required when creating a new user
    required: false
  description:
    description:
      - Description of the user
    required: false
  admin:
    description:
      - Whether or not the user is an administrator
    required: false
    default: false
    type: bool
  user_password:
    description:
      - Password for the user
    required: false
  default_location:
    description:
      - The location that the user uses by default
    required: false
  default_organization:
    description:
      - The organizxation that the user uses by default
    required: false
  auth_source:
    description:
      - Authentication source where the user exists
    required: false
    default: Internal
  timezone:
    description:
      - Timezone for the user
      - If blank it will use the browser timezone.
    required: false
  locale:
    description:
      - The language locale for the user
    required: false
  roles:
    description:
      - List of roles assigned to the user
    required: false
    type: list
  locations:
    description:
      - List of locations assigned to the user
    required: false
    type: list
  organizations:
    description:
      - List of organizations assigned to the user
    required: false
    type: list
  state:
    description:
      - State of the user
    default: present
    choices:
      - present
      - absent
'''

EXAMPLES = '''
- name: Create a user
  foreman_user:
    name: test
    firstname: Test
    lastname: Userson
    mail: test.userson@example.com
    description: Dr. Test Userson
    admin: no
    user_password: s3cret
    default_location: Test Location
    default_organization: Test Organization
    auth_source: Internal
    timezone: Stockholm
    locale: sv_SE
    roles:
      - Manager
    locations:
      - Test Location
    organizations:
      - Test Organization
    state: present

- name: Update a user
  foreman_user:
    name: test
    firstname: Tester
    state: present

- name: Change password
  foreman_user:
    name: test
    user_password: newp@ss

'''

RETURN = ''' # '''

from ansible.module_utils.foreman_helper import (
    sanitize_entity_dict,
    ForemanEntityApypieAnsibleModule,
)

# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'login',
    'firstname': 'firstname',
    'lastname': 'lastname',
    'mail': 'mail',
    'description': 'description',
    'admin': 'admin',
    'user_password': 'password',
    'default_location': 'default_location_id',
    'default_organization': 'default_organization_id',
    'auth_source': 'auth_source_id',
    'timezone': 'timezone',
    'locale': 'locale',
    'roles': 'role_ids',
    'locations': 'location_ids',
    'organizations': 'organization_ids',
}

# List of allowed timezones
timezone_list = [
  'International Date Line West',
  'American Samoa',
  'Midway Island',
  'Hawaii',
  'Alaska',
  'Pacific Time (US &amp; Canada)',
  'Tijuana',
  'Arizona',
  'Chihuahua',
  'Mazatlan',
  'Mountain Time (US &amp; Canada)',
  'Central America',
  'Central Time (US &amp; Canada)',
  'Guadalajara',
  'Mexico City',
  'Monterrey',
  'Saskatchewan',
  'Bogota',
  'Eastern Time (US &amp; Canada)',
  'Indiana (East)',
  'Lima',
  'Quito',
  'Atlantic Time (Canada)',
  'Caracas',
  'Georgetown',
  'La Paz',
  'Puerto Rico',
  'Santiago',
  'Newfoundland',
  'Brasilia',
  'Buenos Aires',
  'Greenland',
  'Montevideo',
  'Mid-Atlantic',
  'Azores',
  'Cape Verde Is.',
  'Dublin',
  'Edinburgh',
  'Lisbon',
  'London',
  'Monrovia',
  'UTC',
  'Amsterdam',
  'Belgrade',
  'Berlin',
  'Bern',
  'Bratislava',
  'Brussels',
  'Budapest',
  'Casablanca',
  'Copenhagen',
  'Ljubljana',
  'Madrid',
  'Paris',
  'Prague',
  'Rome',
  'Sarajevo',
  'Skopje',
  'Stockholm',
  'Vienna',
  'Warsaw',
  'West Central Africa',
  'Zagreb',
  'Zurich',
  'Athens',
  'Bucharest',
  'Cairo',
  'Harare',
  'Helsinki',
  'Jerusalem',
  'Kaliningrad',
  'Kyiv',
  'Pretoria',
  'Riga',
  'Sofia',
  'Tallinn',
  'Vilnius',
  'Baghdad',
  'Istanbul',
  'Kuwait',
  'Minsk',
  'Moscow',
  'Nairobi',
  'Riyadh',
  'St. Petersburg',
  'Tehran',
  'Abu Dhabi',
  'Baku',
  'Muscat',
  'Samara',
  'Tbilisi',
  'Volgograd',
  'Yerevan',
  'Kabul',
  'Ekaterinburg',
  'Islamabad',
  'Karachi',
  'Tashkent',
  'Chennai',
  'Kolkata',
  'Mumbai',
  'New Delhi',
  'Sri Jayawardenepura',
  'Kathmandu',
  'Almaty',
  'Astana',
  'Dhaka',
  'Urumqi',
  'Rangoon',
  'Bangkok',
  'Hanoi',
  'Jakarta',
  'Krasnoyarsk',
  'Novosibirsk',
  'Beijing',
  'Chongqing',
  'Hong Kong',
  'Irkutsk',
  'Kuala Lumpur',
  'Perth',
  'Singapore',
  'Taipei',
  'Ulaanbaatar',
  'Osaka',
  'Sapporo',
  'Seoul',
  'Tokyo',
  'Yakutsk',
  'Adelaide',
  'Darwin',
  'Brisbane',
  'Canberra',
  'Guam',
  'Hobart',
  'Melbourne',
  'Port Moresby',
  'Sydney',
  'Vladivostok',
  'Magadan',
  'New Caledonia',
  'Solomon Is.',
  'Srednekolymsk',
  'Auckland',
  'Fiji',
  'Kamchatka',
  'Marshall Is.',
  'Wellington',
  'Chatham Is.',
  'Nuku&#39;alofa',
  'Samoa',
  'Tokelau Is.',
]

# List of allowed locales
locale_list = [
  'ca',
  'de',
  'en',
  'en_GB',
  'es',
  'fr',
  'gl',
  'it',
  'ja',
  'ko',
  'nl_NL',
  'pl',
  'pt_BR',
  'ru',
  'sv_SE',
  'zh_CN',
  'zh_TW',
]

def main():
    module = ForemanEntityApypieAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            firstname=dict(required=False),
            lastname=dict(required=False),
            mail=dict(required=False),
            description=dict(required=False),
            admin=dict(required=False, type='bool', default=False),
            user_password=dict(required=False, no_log=True),
            default_location=dict(required=False),
            default_organization=dict(required=False),
            auth_source=dict(required=False),
            timezone=dict(required=False, choices=timezone_list),
            locale=dict(required=False, choices=locale_list),
            roles=dict(required=False, type='list'),
            locations=dict(required=False, type='list'),
            organizations=dict(required=False, type='list')
        ),
        supports_check_mode=True,
    )

    (entity_dict, state) = module.parse_params()

    module.connect()

    search = 'login="{}"'.format(entity_dict['name'])
    entity = module.find_resource('users', search, failsafe=True)

    if 'mail' not in entity_dict:
        entity_dict['mail'] = entity['mail']

    if 'default_location' in entity_dict:
        entity_dict['default_location'] = module.find_resource_by_name('locations', entity_dict['default_location'], thin=True)['id']

    if 'default_organization' in entity_dict:
        entity_dict['default_organization'] = module.find_resource_by_name('organizations', entity_dict['default_organization'], thin=True)['id']

    if 'auth_source' in entity_dict:
        entity_dict['auth_source'] = module.find_resource_by_name('auth_sources', entity_dict['auth_source'], thin=True)['id']

    if 'roles' in entity_dict:
        entity_dict['roles'] = module.find_resources('roles', entity_dict['roles'], thin=True)

    if 'locations' in entity_dict:
        entity_dict['locations'] = module.find_resources('locations', entity_dict['locations'], thin=True)

    if 'organizations' in entity_dict:
        entity_dict['organizations'] = module.find_resources('organizations', entity_dict['organizations'], thin=True)

    entity_dict = sanitize_entity_dict(entity_dict, name_map)

    check_missing = None
    if 'password' in entity_dict:
      check_missing = ['password']

    changed = module.ensure_resource_state('users', entity_dict, entity, state,
      check_missing=check_missing)

    module.exit_json(changed=changed, entity_dict=entity_dict)


if __name__ == '__main__':
    main()

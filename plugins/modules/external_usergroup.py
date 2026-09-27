#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Kirill Shirinkin (kirill@mkdev.me)
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
module: external_usergroup
version_added: 1.0.0
short_description: Manage External User Groups
description:
  - Create, update, and delete external user groups
author:
  - "Kirill Shirinkin (@Fodoj)"
options:
  name:
    description:
      - Name of the group
    required: true
    type: str
  usergroup:
    description:
      - Name of the linked usergroup
    required: true
    type: str
  auth_source:
    description:
      - Name of the authentication source to be used for this group
    required: true
    type: str
    aliases:
      - auth_source_ldap
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
'''

EXAMPLES = '''
- name: Create an external user group
  theforeman.foreman.external_usergroup:
    name: test
    auth_source: "My LDAP server"
    usergroup: "Internal Usergroup"
    state: present
- name: Link a group from FreeIPA
  theforeman.foreman.external_usergroup:
    name: ipa_users
    auth_source: "External"
    usergroup: "Internal Usergroup"
    state: present
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    external_usergroups:
      description: List of external usergroups.
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanEntityAnsibleModule


def _external_usergroup_auth_source_id(external_usergroup):
    if external_usergroup.get('auth_source_id') is not None:
        return external_usergroup['auth_source_id']

    for key in ('auth_source', 'auth_source_ldap', 'auth_source_external'):
        auth_source = external_usergroup.get(key)
        if isinstance(auth_source, dict):
            return auth_source.get('id')

    return None


def _find_external_usergroup(external_usergroups, name, auth_source_id):
    for external_usergroup in external_usergroups:
        if (
            external_usergroup['name'] == name
            and _external_usergroup_auth_source_id(external_usergroup) == auth_source_id
        ):
            return external_usergroup

    return None


class ForemanExternalUsergroupModule(ForemanEntityAnsibleModule):
    pass


def main():
    module = ForemanExternalUsergroupModule(
        foreman_spec=dict(
            name=dict(required=True),
            usergroup=dict(required=True, type='entity', ensure=False),
            auth_source=dict(required=True, aliases=['auth_source_ldap'], type='entity', flat_name='auth_source_id', resource_type='auth_sources'),
            auth_source_ldap=dict(type='entity', invisible=True, flat_name='auth_source_id'),
            auth_source_external=dict(type='entity', invisible=True, flat_name='auth_source_id'),
        ),
    )

    with module.api_connection():
        params = module.scope_for('usergroup')
        external_usergroups = module.list_resource("external_usergroups", params=params)
        auth_source = module.lookup_entity('auth_source')

        # There is no way to find by name via API search, so we need
        # to iterate over all external user groups of a given usergroup
        entity = _find_external_usergroup(external_usergroups, module.foreman_params['name'], auth_source['id'])

        module.set_entity('entity', entity)

        if auth_source.get('type') == 'AuthSourceExternal':
            module.set_entity('auth_source_external', auth_source)
        elif auth_source.get('type') == 'AuthSourceLdap':
            module.set_entity('auth_source_ldap', auth_source)
        else:
            module.fail_json(msg="Unsupported authentication source type: {0}".format(auth_source.get('type')))

        module.run(params=params)


if __name__ == '__main__':
    main()

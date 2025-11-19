#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) Evgeni Golov
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
module: smart_proxy_refresh
version_added: 5.9.0
short_description: Refresh Smart Proxy features
description:
  - Refresh Smart Proxy features
author:
  - "Evgeni Golov (@evgeni)"
options:
  smart_proxy:
    description:
      - Name of the Smart Proxy
    required: true
    type: str
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.taxonomy
'''

EXAMPLES = '''
- name: "Refresh Smart Proxy"
  theforeman.foreman.smart_proxy_refresh:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    smart_proxy: "foreman-proxy.example.com"
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    smart_proxies:
      description: List of smart_proxies.
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanTaxonomicAnsibleModule


class ForemanSmartProxyRefreshModule(ForemanTaxonomicAnsibleModule):
    pass


def main():
    module = ForemanSmartProxyRefreshModule(
        foreman_spec=dict(
            smart_proxy=dict(type='entity', required=True),
        ),
        supports_check_mode=False,
    )

    with module.api_connection():
        smart_proxy = module.lookup_entity('smart_proxy')
        entity = module.resource_action('smart_proxies', 'refresh', {'id': smart_proxy['id']})
        module.exit_json(entity=entity)


if __name__ == '__main__':
    main()

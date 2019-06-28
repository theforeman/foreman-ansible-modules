#!/usr/bin/python
# -*- coding: utf-8 -*-
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
module: smart_proxy
version_added: 1.4.0
short_description: Manage Smart Proxies
description:
  - Create, update and delete Smart Proxies
author:
  - "James Stuart (@jstuart)"
  - "Matthias M Dellweg (@mdellweg)"
options:
  name:
    description:
      - Name of the Smart Proxy
    required: true
    type: str
  url:
    description:
      - URL of the Smart Proxy
    required: true
    type: str
  download_policy:
    description:
      - The download policy for the Smart Proxy
      - Only available for Katello installations.
    choices:
      - background
      - immediate
      - on_demand
    required: false
    type: str
notes:
  - Even with I(state=present) this module does not install a new Smart Proxy.
  - It can only associate an existing Smart Proxy listening at the specified I(url).
  - Consider using I(foreman-installer) to create Smart Proxies.
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.taxonomy
'''

EXAMPLES = '''
# Create a local Smart Proxy
- name: "Create Smart Proxy"
  theforeman.foreman.foreman_smart_proxy:
    username: "admin"
    password: "changeme"
    server_url: "https://{{ ansible_fqdn }}"
    name: "{{ ansible_fqdn }}"
    url: "https://{{ ansible_fqdn }}:9090"
    download_policy: "immediate"
    organizations:
      - "Default Organization"
    locations:
      - "Default Location"
    state: present
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


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanTaxonomicEntityAnsibleModule


class ForemanSmartProxyModule(ForemanTaxonomicEntityAnsibleModule):
    pass


def main():
    module = ForemanSmartProxyModule(
        foreman_spec=dict(
            name=dict(required=True),
            url=dict(required=True),
            download_policy=dict(required=False, choices=['background', 'immediate', 'on_demand']),
        ),
        required_plugins=[('katello', ['download_policy'])],
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()

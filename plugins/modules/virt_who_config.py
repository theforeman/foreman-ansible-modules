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
module: virt_who_config
version_added: 3.15.0
short_description: Manage Virt Who Configs
description:
  - Manage Virt Who Configs
author:
  - "Dirk Goetz (@dgoetz)"
options:
  name:
    description:
      - The name of the Virt Who Configuration
    type: str
    required: true
  interval:
    description:
      - The interval to run Virt Who
    choices:
      - 60
      - 120
      - 240
      - 480
      - 720
      - 1440
      - 2880
      - 4320
    type: int
    required: true
  filtering_mode:
    description:
      - The filtering mode for Hypervisors
      - 0 means no filtering, 1 means whitelist, 2 means blacklist
    choices:
      - 0
      - 1
      - 2
    type: int
    required: true
  whitelist:
    description:
      - Hypervisor whitelist, applicable only when filtering mode is set to 1
      - Wildcards and regular expressions are supported, multiple records must be separated by comma
    type: str
  blacklist:
    description:
      - Hypervisor blacklist, applicable only when filtering mode is set to 2
      - Wildcards and regular expressions are supported, multiple records must be separated by comma
    type: str
  filter_host_parents:
    description:
      - Applicable only for esx provider type
      - Only hosts which parent (usually ComputeResource) name is specified in comma-separated list in this option will be reported
      - Wildcards and regular expressions are supported, multiple records must be separated by comma
      - Put the value into the double-quotes if it contains special characters like comma
      - All new line characters will be removed in resulting configuration file, white spaces are removed from beginning and end
    type: str
  exclude_host_parents:
    description:
      - Applicable only for esx provider type
      - Hosts which parent (usually ComputeResource) name is specified in comma-separated list in this option will NOT be reported
      - Wildcards and regular expressions are supported, multiple records must be separated by comma
      - Put the value into the double-quotes if it contains special characters like comma
      - All new line characters will be removed in resulting configuration file, white spaces are removed from beginning and end
    type: str
  hypervisor_id:
    description:
      - Specifies how the hypervisor will be identified
    choices:
      - hostname
      - uuid
      - hwuuid
    type: str
    required: true
  hypervisor_type:
    description:
      - Hypervisor type
    choices:
      - esx
      - hyperv
      - libvirt
      - kubevirt
      - ahv
    type: str
    required: true
  hypervisor_server:
    description:
      - Fully qualified host name or IP address of the hypervisor
    type: str
  hypervisor_username:
    description:
      - Account name by which virt-who is to connect to the hypervisor
    type: str
  hypervisor_password:
    description:
      - Hypervisor password, required for all hypervisor types except for libvirt/kubevirt
    type: str
  satellite_url:
    description:
      - Foreman server FQDN
    type: str
    required: true
  debug:
    description:
      - Enable debugging output
    type: bool
  kubeconfig_path:
    description:
      - Configuration file containing details about how to connect to the cluster and authentication details
    type: str
  http_proxy_id:
    description:
      - HTTP proxy that should be used for communication between the server on which virt-who is running and the hypervisors and virtualization managers
    type: str
  no_proxy:
    description:
      - A comma-separated list of hostnames or domains or ip addresses to ignore proxy settings for
      - Optionally this may be set to * to bypass proxy settings for all hostnames domains or ip addresses
    type: str
  prism_flavor:
    description:
      - Select the Prism flavor you are connecting to
    choices:
      - central
      - element
    type: str
  ahv_internal_debug:
    description:
      - Enable debugging output is required to enable AHV internal debug
      - It provides extra AHV debug information when both options are enabled
    type: bool
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.organization
  - theforeman.foreman.foreman.entity_state
'''

EXAMPLES = '''
- name: "Create a Virt Who Configuration"
  theforeman.foreman.virt_who_config:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    name: "A Virt Who Configuration"
    interval: 120
    filtering_mode: 0
    hypervisor_id: "hostname"
    hypervisor_type: "libvirt"
    satellite_url: "foreman.example.com"
    state: "present"
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    activation_keys:
      description: List of Virt Who Configs
      type: list
      elements: dict
'''


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloEntityAnsibleModule


class KatelloConfigModule(KatelloEntityAnsibleModule):
    pass


def main():
    module = KatelloConfigModule(
        foreman_spec=dict(
            name=dict(required=True),
            interval=dict(required=True, type='int', choices=[60, 120, 240, 480, 720, 1440, 2880, 4320]),
            filtering_mode=dict(required=True, type='int', choices=[0, 1, 2]),
            whitelist=dict(),
            blacklist=dict(),
            filter_host_parents=dict(),
            exclude_host_parents=dict(),
            hypervisor_id=dict(required=True, choices=['hostname', 'uuid', 'hwuuid']),
            hypervisor_type=dict(required=True, choices=['esx', 'hyperv', 'libvirt', 'kubevirt', 'ahv']),
            hypervisor_server=dict(),
            hypervisor_username=dict(),
            hypervisor_password=dict(no_log=True),
            satellite_url=dict(required=True),
            debug=dict(type='bool'),
            kubeconfig_path=dict(),
            http_proxy_id=dict(type='entity', resource_type='http_proxies', scope=['organization']),
            no_proxy=dict(),
            prism_flavor=dict(choices=['central', 'element']),
            ahv_internal_debug=dict(type='bool'),
        ),
    )
    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()

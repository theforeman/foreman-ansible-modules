#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2022 William Bradford Clark
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
module: alternate_content_source_info
version_added: 3.8.0
short_description: Fetch information about Alternate Content Sources
description:
  - Fetch information about Alternate Content Sources
author: "William Bradford Clark (@wbclark)"
options:
  name:
    description:
      - Name of the Alternate Content Source
    required: false
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.katelloinfomodule
  - theforeman.foreman.foreman.infomodule
'''

EXAMPLES = '''
- name: "Find Alternate Content Source by name."
  theforeman.foreman.alternate_content_source_info:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    name: "Baby's First ACS"
'''

RETURN = '''
alternate_content_source:
  description: Details about the found Alternate Content Source.
  returned: success and I(name) was passed
  type: dict
alternate_content_sources:
  description: List of all found Alternate Content Sources and their details.
  returned: success and I(search) was passed
  type: list
  elements: dict
'''


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloInfoAnsibleModule


class KatelloAlternateContentSourceInfo(KatelloInfoAnsibleModule):
    pass


def main():
    module = KatelloAlternateContentSourceInfo()

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()

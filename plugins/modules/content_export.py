#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2022, Jeremy Lenz <jlenz@redhat.com>
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
module: content_export
version_added: 3.5.0
short_description: Manage pulp3 content exports
description:
    - Export content view versions, repositories, or library content to a directory.
author:
    - "Jeremy Lenz (@jeremylenz)"

'''


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloAnsibleModule, _flatten_entity


class KatelloContentExportModule(KatelloAnsibleModule):
    pass


def main():
    module = KatelloContentExportModule(
        foreman_spec=dict(
            destination_server=dict(required=False, type='str'),
            chunk_size_gb=dict(required=False, type='int'),
            fail_on_missing_content=dict(required=False, type='bool'),
        ),
    )

    with module.api_connection():
        module.auto_lookup_entities()
        payload = _flatten_entity(module.foreman_params, module.foreman_spec)
        task = module.resource_action('content_exports', 'library', payload)

        module.exit_json(task=task)


if __name__ == '__main__':
    main()

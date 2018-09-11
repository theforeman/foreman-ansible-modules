#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2016, Eric D Helms <ericdhelms@gmail.com>
# (c) 2018, Sean O'Keeffe <seanokeeffe797@gmail.com>
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

DOCUMENTATION = '''
---
module: katello_upload
short_description: Upload content to Katello
description:
    - Allows the upload of content to a Katello repository
author: "Eric D Helms (@ehelms)"
requirements:
    - "nailgun >= 0.28.0"
    - "python >= 2.6"
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
    verify_ssl:
        description:
            - Verify SSL of the Foreman server
        required: false
        default: true
        type: bool
    src:
        description:
            - File to upload
        required: true
        type: path
        aliases:
          - file
    repository:
        description:
            - Repository to upload file in to
        required: true
    product:
        description:
            - Product to which the repository lives in
        required: true
    organization:
        description:
            - Organization that the Product is in
        required: true
notes:
    - Currently only idempotent when uploading a RPM
'''

EXAMPLES = '''
- name: "Upload my.rpm"
  katello_upload:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    src: "my.rpm"
    repository: "Build RPMs"
    product: "My Product"
    organization: "Default Organization"
'''

RETURN = '''# '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        create_server,
        ping_server,
        find_organization,
        find_product,
        find_repository,
        find_package,
    )

    from nailgun.entities import (
        ContentUpload,
    )
    from subprocess import check_output
    has_import_error = False
except ImportError as e:
    has_import_error = True
    import_error_msg = str(e)

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native


def upload(module, src, repository):
    content_upload = ContentUpload(repository=repository)
    if not module.check_mode:
        content_upload.upload(src)
    return True


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            src=dict(required=True, type='path', aliases=['file']),
            repository=dict(required=True),
            product=dict(required=True),
            organization=dict(required=True),
        ),
        supports_check_mode=True,
    )

    if has_import_error:
        module.fail_json(msg=import_error_msg)

    entity_dict = dict(
        [(k, v) for (k, v) in module.params.items() if v is not None])

    server_url = entity_dict.pop('server_url')
    username = entity_dict.pop('username')
    password = entity_dict.pop('password')
    verify_ssl = entity_dict.pop('verify_ssl')

    try:
        create_server(server_url, (username, password), verify_ssl)
    except Exception as e:
        module.fail_json(msg="Failed to connect to Foreman server: %s " % e)

    ping_server(module)

    entity_dict['organization'] = find_organization(module, name=entity_dict['organization'])
    entity_dict['product'] = find_product(module, name=entity_dict['product'], organization=entity_dict['organization'])
    entity_dict['repository'] = find_repository(module, name=entity_dict['repository'], product=entity_dict['product'])

    package = False
    if entity_dict['repository'].content_type == "yum":
        name, version, release, arch = check_output("rpm --queryformat '%%{NAME} %%{VERSION} %%{RELEASE} %%{ARCH}' -qp %s" % entity_dict['src'],
                                                    shell=True).split()
        query = "name = \"{}\" and version = \"{}\" and release = \"{}\" and arch = \"{}\"".format(name, version, release, arch)
        package = find_package(module, query, repository=entity_dict['repository'], failsafe=True)

    changed = False
    if package is None or package is False:
        try:
            changed = upload(module, entity_dict['src'], entity_dict['repository'])
        except Exception as e:
            module.fail_json(msg=to_native(e))

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()

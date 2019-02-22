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
    - "ansible >= 2.3"
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
    - Currently only idempotent when uploading to an RPM & file repository
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
        find_organization,
        find_product,
        find_repository,
        find_package,
        find_file,
    )

    from nailgun.entities import (
        ContentUpload,
    )
    from subprocess import check_output
    import os
    import hashlib
except ImportError:
    pass

from ansible.module_utils.foreman_helper import ForemanAnsibleModule
from ansible.module_utils._text import to_native


def upload(module, src, repository):
    content_upload = ContentUpload(repository=repository)
    if not module.check_mode:
        content_upload.upload(src)
    return True


def main():
    module = ForemanAnsibleModule(
        argument_spec=dict(
            src=dict(required=True, type='path', aliases=['file']),
            repository=dict(required=True),
            product=dict(required=True),
            organization=dict(required=True),
        ),
        supports_check_mode=True,
    )

    entity_dict = module.parse_params()

    module.connect()

    entity_dict['organization'] = find_organization(module, name=entity_dict['organization'])
    entity_dict['product'] = find_product(module, name=entity_dict['product'], organization=entity_dict['organization'])
    entity_dict['repository'] = find_repository(module, name=entity_dict['repository'], product=entity_dict['product'])

    content_unit = None
    if entity_dict['repository'].content_type == "yum":
        name, version, release, arch = check_output("rpm --queryformat '%%{NAME} %%{VERSION} %%{RELEASE} %%{ARCH}' -qp %s" % entity_dict['src'],
                                                    shell=True).decode('ascii').split()
        query = "name = \"{}\" and version = \"{}\" and release = \"{}\" and arch = \"{}\"".format(name, version, release, arch)
        content_unit = find_package(module, query, repository=entity_dict['repository'], failsafe=True)
    elif entity_dict['repository'].content_type == "file":
        h = hashlib.sha256()
        with open(entity_dict['src'], "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        checksum = h.hexdigest()
        name = os.path.basename(entity_dict['src'])
        query = "name = \"{}\" and checksum = \"{}\"".format(name, checksum)
        content_unit = find_file(module, query, repository=entity_dict['repository'], failsafe=True)

    changed = False
    if not content_unit:
        try:
            changed = upload(module, entity_dict['src'], entity_dict['repository'])
        except Exception as e:
            module.fail_json(msg=to_native(e))

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()

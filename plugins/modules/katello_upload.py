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
    - "apypie"
options:
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
extends_documentation_fragment: foreman
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

RETURN = ''' # '''

from subprocess import check_output
import os
import hashlib

from ansible.module_utils.foreman_helper import ForemanApypieAnsibleModule


def main():
    module = ForemanApypieAnsibleModule(
        argument_spec=dict(
            src=dict(required=True, type='path', aliases=['file']),
            repository=dict(required=True),
            product=dict(required=True),
            organization=dict(required=True),
        ),
    )

    entity_dict = module.clean_params()

    module.connect()

    entity_dict['organization'] = module.find_resource_by_name('organizations', entity_dict['organization'], thin=True)
    scope = {'organization_id': entity_dict['organization']['id']}
    entity_dict['product'] = module.find_resource_by_name('products', entity_dict['product'], params=scope, thin=True)
    product_scope = {'product_id': entity_dict['product']['id']}
    entity_dict['repository'] = module.find_resource_by_name('repositories', entity_dict['repository'], params=product_scope)
    repository_scope = {'repository_id': entity_dict['repository']['id']}

    content_unit = None
    if entity_dict['repository']['content_type'] == 'yum':
        name, version, release, arch = check_output("rpm --queryformat '%%{NAME} %%{VERSION} %%{RELEASE} %%{ARCH}' -qp %s" % entity_dict['src'],
                                                    shell=True).decode('ascii').split()
        # this is missing epoch
        query = 'name = "{}" and version = "{}" and release = "{}" and arch = "{}"'.format(name, version, release, arch)
        content_unit = module.find_resource('packages', query, params=repository_scope, failsafe=True)
    elif entity_dict['repository']['content_type'] == 'file':
        h = hashlib.sha256()
        with open(entity_dict['src'], "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        checksum = h.hexdigest()
        name = os.path.basename(entity_dict['src'])
        query = 'name = "{}" and checksum = "{}"'.format(name, checksum)
        content_unit = module.find_resource('file_units', query, params=repository_scope, failsafe=True)
    else:
        # possible types in 3.12: docker, ostree, yum, puppet, file, deb
        module.fail_json("Uploading to a {} repository is not supported yet.".format(entity_dict['repository']['content_type']))

    changed = False
    if not content_unit:
        _, content_upload = module.resource_action('content_uploads', 'create', repository_scope)
        content_upload_scope = {'id': content_upload['upload_id']}
        content_upload_scope.update(repository_scope)
        filename = os.path.basename(entity_dict['src'])

        offset = 0
        content_chunk_size = 2 * 1024 * 1024
        checksum = hashlib.sha256()

        with open(entity_dict['src'], 'rb') as contentfile:
            chunk = contentfile.read(content_chunk_size)
            while len(chunk) > 0:
                data = {'content': chunk, 'offset': offset}
                module.resource_action('content_uploads', 'update', params=content_upload_scope, options={'skip_validation': True}, data=data)

                offset += len(chunk)
                checksum.update(chunk)
                chunk = contentfile.read(content_chunk_size)

        uploads = [{'id': content_upload['upload_id'], 'name': filename,
                    'size': offset, 'checksum': checksum.hexdigest()}]
        import_params = {'id': entity_dict['repository']['id'], 'uploads': uploads}
        module.resource_action('repositories', 'import_uploads', import_params)

        module.resource_action('content_uploads', 'destroy', content_upload_scope)

        changed = True

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()

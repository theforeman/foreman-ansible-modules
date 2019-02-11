# -*- coding: utf-8 -*-
# (c) Matthias Dellweg (ATIX AG) 2017

import re
import yaml
import traceback

from ansible.module_utils.basic import AnsibleModule

try:
    import ansible.module_utils.ansible_nailgun_cement
    HAS_NAILGUN = True
except ImportError:
    HAS_NAILGUN = False
    NAILGUN_IMP_ERR = traceback.format_exc()


class ForemanAnsibleModule(AnsibleModule):

    def __init__(self, argument_spec, **kwargs):
        args = dict(
            server_url=dict(required=True),
            username=dict(required=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            state=dict(choices=['present', 'absent'], default='present'),
        )
        args.update(argument_spec)
        super(ForemanAnsibleModule, self).__init__(argument_spec=args, **kwargs)

        if not HAS_NAILGUN:
            self.fail_json(msg='The nailgun Python module is required',
                           exception=NAILGUN_IMP_ERR)

    def parse_params(self):
        module_params = self.filter_module_params()
        server_params = self.get_server_params(module_params)
        return (server_params, module_params)

    def filter_module_params(self):
        return {k: v for (k, v) in self.params.items() if v is not None}

    def get_server_params(self, module_params):
        server_url = module_params.pop('server_url')
        username = module_params.pop('username')
        password = module_params.pop('password')
        verify_ssl = module_params.pop('verify_ssl')
        return (server_url, username, password, verify_ssl)


# Helper for templates
def parse_template(template_content, module):
    try:
        template_dict = {}
        data = re.search(
            r'<%#([^%]*([^%]*%*[^>%])*%*)%>', template_content)
        if data:
            datalist = data.group(1)
            if datalist[-1] == '-':
                datalist = datalist[:-1]
            template_dict = yaml.safe_load(datalist)
        # No metadata, import template anyway
        template_dict['template'] = template_content
    except Exception as e:
        module.fail_json(msg='Error while parsing template: ' + str(e))
    return template_dict


def parse_template_from_file(file_name, module):
    try:
        with open(file_name) as input_file:
            template_content = input_file.read()
            template_dict = parse_template(template_content, module)
    except Exception as e:
        module.fail_json(msg='Error while reading template file: ' + str(e))
    return template_dict


# Helper for titles
def split_fqn(title):
    """ Split fully qualified name (title) in parent title and name """
    fqn = title.split('/')
    if len(fqn) > 1:
        name = fqn.pop()
        return ('/'.join(fqn), name)
    else:
        return (None, title)


def build_fqn(name_or_title, parent=None):
    if '/' not in name_or_title and parent:
        return "%s/%s" % (parent, name_or_title)
    else:
        return name_or_title

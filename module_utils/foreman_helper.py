# -*- coding: utf-8 -*-
# (c) Matthias Dellweg (ATIX AG) 2017

import re
import yaml
import traceback

from ansible.module_utils.basic import AnsibleModule

try:
    import ansible.module_utils.ansible_nailgun_cement
    from nailgun import entity_mixins
    from nailgun.config import ServerConfig
    from nailgun.entities import Ping
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
        )
        args.update(argument_spec)
        super(ForemanAnsibleModule, self).__init__(argument_spec=args, **kwargs)

        self.check_requirements()

        self._foremanapi_server_url = self.params.pop('server_url')
        self._foremanapi_username = self.params.pop('username')
        self._foremanapi_password = self.params.pop('password')
        self._foremanapi_verify_ssl = self.params.pop('verify_ssl')

    def check_requirements(self):
        if not HAS_NAILGUN:
            self.fail_json(msg='The nailgun Python module is required',
                           exception=NAILGUN_IMP_ERR)

    def parse_params(self):
        return self.filter_module_params()

    def filter_module_params(self):
        return {k: v for (k, v) in self.params.items() if v is not None}

    def get_server_params(self):
        return (self._foremanapi_server_url, self._foremanapi_username, self._foremanapi_password, self._foremanapi_verify_ssl)

    def connect(self, ping=True):
        entity_mixins.DEFAULT_SERVER_CONFIG = ServerConfig(
            url=self._foremanapi_server_url,
            auth=(self._foremanapi_username, self._foremanapi_password),
            verify=self._foremanapi_verify_ssl,
        )

        if ping:
            self.ping()

    def ping(self):
        try:
            return Ping().search_json()
        except Exception as e:
            self.fail_json(msg="Failed to connect to Foreman server: %s " % e)


class ForemanEntityAnsibleModule(ForemanAnsibleModule):

    def __init__(self, argument_spec, **kwargs):
        args = dict(
            state=dict(choices=['present', 'absent'], default='present'),
        )
        args.update(argument_spec)
        super(ForemanEntityAnsibleModule, self).__init__(argument_spec=args, **kwargs)

    def parse_params(self):
        module_params = super(ForemanEntityAnsibleModule, self).parse_params()
        state = module_params.pop('state')
        return (module_params, state)


class KatelloEntityAnsibleModule(ForemanEntityAnsibleModule):

    def __init__(self, argument_spec, **kwargs):
        args = dict(
            organization=dict(required=True),
        )
        args.update(argument_spec)
        super(KatelloEntityAnsibleModule, self).__init__(argument_spec=args, **kwargs)


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

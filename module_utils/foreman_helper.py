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

try:
    import apypie
    HAS_APYPIE = True
except ImportError:
    HAS_APYPIE = False
    APYPIE_IMP_ERR = traceback.format_exc()


class ForemanBaseAnsibleModule(AnsibleModule):

    def __init__(self, argument_spec, **kwargs):
        args = dict(
            server_url=dict(required=True),
            username=dict(required=True),
            password=dict(required=True, no_log=True),
            validate_certs=dict(type='bool', default=True, aliases=['verify_ssl']),
        )
        args.update(argument_spec)
        super(ForemanBaseAnsibleModule, self).__init__(argument_spec=args, **kwargs)

        self.check_requirements()

        self._foremanapi_server_url = self.params.pop('server_url')
        self._foremanapi_username = self.params.pop('username')
        self._foremanapi_password = self.params.pop('password')
        self._foremanapi_validate_certs = self.params.pop('validate_certs')

    def parse_params(self):
        return self.filter_module_params()

    def filter_module_params(self):
        return {k: v for (k, v) in self.params.items() if v is not None}

    def get_server_params(self):
        return (self._foremanapi_server_url, self._foremanapi_username, self._foremanapi_password, self._foremanapi_validate_certs)


def _exception2fail_json(msg='Generic failure: %s'):
    def decor(f):
        def inner(self, *args, **kwargs):
            try:
                return f(self, *args, **kwargs)
            except Exception as e:
                self.fail_json(msg=msg % e)
        return inner
    return decor


class ForemanAnsibleModule(ForemanBaseAnsibleModule):

    def check_requirements(self):
        if not HAS_NAILGUN:
            self.fail_json(msg='The nailgun Python module is required',
                           exception=NAILGUN_IMP_ERR)

    def connect(self, ping=True):
        entity_mixins.DEFAULT_SERVER_CONFIG = ServerConfig(
            url=self._foremanapi_server_url,
            auth=(self._foremanapi_username, self._foremanapi_password),
            verify=self._foremanapi_validate_certs,
        )

    @_exception2fail_json(msg="Failed to connect to Foreman server: %s ")
    def ping(self):
        return Ping().search_json()


class ForemanApypieAnsibleModule(ForemanBaseAnsibleModule):

    def check_requirements(self):
        if not HAS_APYPIE:
            self.fail_json(msg='The apypie Python module is required',
                           exception=APYPIE_IMP_ERR)

    @_exception2fail_json(msg="Failed to connect to Foreman server: %s ")
    def connect(self, ping=True):
        self.foremanapi = apypie.Api(
            uri=self._foremanapi_server_url,
            username=self._foremanapi_username,
            password=self._foremanapi_password,
            api_version=2,
            verify_ssl=self._foremanapi_validate_certs,
        )

        if ping:
            self.ping()

    @_exception2fail_json(msg="Failed to connect to Foreman server: %s ")
    def ping(self):
        return self.foremanapi.resource('home').call('status')

    @_exception2fail_json('Failed to show resource: %s')
    def show_resource(self, resource, resource_id):
        return self.foremanapi.resource(resource).call('show', {'id': resource_id})

    @_exception2fail_json(msg='Failed to list resource: %s')
    def list_resource(self, resource, search, params=None):
        if params is None:
            params = {}
        params['search'] = search
        params['per_page'] = 2 << 31
        return self.foremanapi.resource(resource).call('index', params)['results']

    def find_resource(self, resource, search, params=None, failsafe=False, thin=False):
        if params is None:
            params = {}
        params['thin'] = thin
        results = self.list_resource(resource, search, params)
        if len(results) == 1:
            result = results[0]
        elif failsafe:
            result = None
        else:
            self.fail_json(msg="No data found for %s" % search)
        if result:
            if thin:
                result = {'id': result['id']}
            else:
                result = self.show_resource(resource, result['id'])
        return result

    def find_resource_by_name(self, resource, name, params=None, failsafe=False, thin=False):
        search = 'name="{}"'.format(name)
        return self.find_resource(resource, search, params, failsafe, thin)

    def find_resources(self, resource, search_list, failsafe=False, thin=False):
        return [self.find_resource_by_name(resource, search_item, failsafe=failsafe, thin=thin) for search_item in search_list]

    def create_resource(self, resource, entity_dict):
        new_entity = {}
        # FIXME: (?) entity_dict can contain other resources, when it does, translate these entries to only list their IDs
        for key, value in entity_dict.items():
            new_entity[key] = self._flatten_value(value)
        return self._resource_action(resource, 'create', new_entity)

    def delete_resource(self, resource, resource_id):
        return self._resource_action(resource, 'destroy', {'id': resource_id})

    def update_resource(self, resource, old_entity, entity_dict, check_missing, check_type, force_update):
        # FIXME: I am not sure this *whole* method is required as-is. It's mostly copied from the nailgun lib.
        entity_id = old_entity.pop('id')
        volatile_entity = old_entity.copy()
        result = volatile_entity
        fields = []
        for key, value in volatile_entity.items():
            if key in entity_dict:
                new_value = entity_dict[key]
                if check_type and not isinstance(value, type(new_value)):
                    if isinstance(value, bool):
                        new_value = boolean(new_value)
                    elif isinstance(value, list):
                        new_value = str(sorted(new_value.split(',')))
                        value = str(sorted([str(v) for v in value]))
                    else:
                        if value is None:
                            value = ""
                        new_value = type(value)(new_value)
                value = self._flatten_value(value)
                new_value = self._flatten_value(new_value)
                if not value == new_value:
                    volatile_entity[key] = new_value
                    fields.append(key)
            # check_missing is a special case, Foreman sometimes returns different values
            # depending on what 'type' of same object you are requesting. Content View
            # Filters are a prime example. We list these attributes in `check_missing`
            # so we can ensure the entity is as the user specified.
            if check_missing is not None and key not in entity_dict and key in check_missing:
                volatile_entity[key] = None
                fields.append(key)
        if force_update:
            for key in force_update:
                fields.append(key)
        if check_missing is not None:
            for key in check_missing:
                if key in entity_dict and key not in volatile_entity.keys():
                    volatile_entity[key] = new_value
                    fields.append(key)
        if len(fields) > 0:
            new_data = {'id': entity_id}
            for key, value in volatile_entity.items():
                if key in fields:
                    new_data[key] = value
            return self._resource_action(resource, 'update', params=new_data)
        return False, result

    def ensure_resource_state(self, resource, entity_dict, entity, state, name_map, check_missing=None, check_type=None, force_update=None):
        changed, _ = self.ensure_resource(resource, entity_dict, entity, state, name_map, check_missing, check_type, force_update)
        return changed

    @_exception2fail_json('Failed to ensure entity state: %s')
    def ensure_resource(self, resource, entity_dict, entity, state, name_map, check_missing=None, check_type=None, force_update=None):
        """ Ensure that a given entity has a certain state """
        changed, changed_entity = False, entity

        entity_dict = sanitize_entity_dict(entity_dict, name_map)

        if state == 'present_with_defaults':
            if entity is None:
                changed, changed_entity = self.create_resource(resource, entity_dict)
        elif state == 'present':
            if entity is None:
                changed, changed_entity = self.create_resource(resource, entity_dict)
            else:
                entity = sanitize_entity_dict(entity, name_map)
                changed, changed_entity = self.update_resource(resource, entity, entity_dict, check_missing, check_type, force_update)
        elif state == 'absent':
            if entity is not None:
                changed, changed_entity = self.delete_resource(resource, entity['id'])
        else:
            self.fail_json(msg='Not a valid state: {}'.format(state))
        return changed, changed_entity

    def _resource_action(self, resource, action, params):
        action_params = self.foremanapi.resource(resource).action(action).params
        resource_payload = self._generate_resource_payload(action_params, params)
        try:
            result = None
            if not self.check_mode:
                result = self.foremanapi.resource(resource).call(action, resource_payload)
        except Exception as e:
            self.fail_json(msg='Error while {}ing {}: {}'.format(
                action, resource, str(e)))
        return True, result

    def _generate_resource_payload(self, action_params, data):
        resource_payload = {}

        for param in action_params:
            if param.expected_type == 'hash':
                resource_payload[param.name] = self._generate_resource_payload(param.params, data)
            elif param.name in data:
                resource_payload[param.name] = data[param.name]

        return resource_payload

    def _flatten_value(self, value):
        if isinstance(value, dict) and 'id' in value:
            value = value['id']
        elif isinstance(value, list) and value and isinstance(value[0], dict) and 'id' in value[0]:
            value = sorted(item['id'] for item in value)
        return value


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


class ForemanEntityApypieAnsibleModule(ForemanApypieAnsibleModule):

    def __init__(self, argument_spec, **kwargs):
        args = dict(
            state=dict(choices=['present', 'absent'], default='present'),
        )
        args.update(argument_spec)
        super(ForemanEntityApypieAnsibleModule, self).__init__(argument_spec=args, **kwargs)

    def parse_params(self):
        module_params = super(ForemanEntityApypieAnsibleModule, self).parse_params()
        state = module_params.pop('state')
        return (module_params, state)


class KatelloEntityApypieAnsibleModule(ForemanEntityApypieAnsibleModule):

    def __init__(self, argument_spec, **kwargs):
        args = dict(
            organization=dict(required=True),
        )
        args.update(argument_spec)
        super(KatelloEntityApypieAnsibleModule, self).__init__(argument_spec=args, **kwargs)


def sanitize_entity_dict(entity_dict, name_map):
    name_map['id'] = 'id'
    return {value: entity_dict[key] for key, value in name_map.items() if key in entity_dict}


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

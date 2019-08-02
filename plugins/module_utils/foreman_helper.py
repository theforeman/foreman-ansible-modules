# -*- coding: utf-8 -*-
# (c) Matthias Dellweg (ATIX AG) 2017

import re
import json
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
        supports_check_mode = kwargs.pop('supports_check_mode', True)
        super(ForemanBaseAnsibleModule, self).__init__(argument_spec=args, supports_check_mode=supports_check_mode, **kwargs)

        self.check_requirements()

        self._foremanapi_server_url = self.params.pop('server_url')
        self._foremanapi_username = self.params.pop('username')
        self._foremanapi_password = self.params.pop('password')
        self._foremanapi_validate_certs = self.params.pop('validate_certs')

    def parse_params(self):
        self.warn("Use of deprecated method parse_params")
        return {k: v for (k, v) in self.params.items() if v is not None}

    def clean_params(self):
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

    def __init__(self, *args, **kwargs):
        super(ForemanApypieAnsibleModule, self).__init__(*args, **kwargs)
        self._thin_default = False
        self.state = 'undefined'
        self.name_map = {}
        self.entity_spec = {}

    def _patch_location_api(self):
        """This is a workaround for the broken taxonomies apidoc in foreman.
            see https://projects.theforeman.org/issues/10359
        """

        _location_organizations_parameter = {
            u'validations': [],
            u'name': u'organization_ids',
            u'show': True,
            u'description': u'\n<p>Organization IDs</p>\n',
            u'required': False,
            u'allow_nil': True,
            u'allow_blank': False,
            u'full_name': u'location[organization_ids]',
            u'expected_type': u'array',
            u'metadata': None,
            u'validator': u'',
        }
        _location_methods = self.foremanapi.apidoc['docs']['resources']['locations']['methods']

        _location_create = next(x for x in _location_methods if x['name'] == 'create')
        _location_create_params_location = next(x for x in _location_create['params'] if x['name'] == 'location')
        _location_create_params_location['params'].append(_location_organizations_parameter)

        _location_update = next(x for x in _location_methods if x['name'] == 'update')
        _location_update_params_location = next(x for x in _location_update['params'] if x['name'] == 'location')
        _location_update_params_location['params'].append(_location_organizations_parameter)

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

        self._patch_location_api()

        if ping:
            self.ping()

    @_exception2fail_json(msg="Failed to connect to Foreman server: %s ")
    def ping(self):
        return self.foremanapi.resource('home').call('status')

    @_exception2fail_json('Failed to show resource: %s')
    def show_resource(self, resource, resource_id, params=None):
        if params is None:
            params = {}
        params['id'] = resource_id
        return self.foremanapi.resource(resource).call('show', params)

    @_exception2fail_json(msg='Failed to list resource: %s')
    def list_resource(self, resource, search=None, params=None):
        if params is None:
            params = {}
        if search is not None:
            params['search'] = search
        params['per_page'] = 2 << 31
        return self.foremanapi.resource(resource).call('index', params)['results']

    def find_resource(self, resource, search, name=None, params=None, failsafe=False, thin=None):
        list_params = {}
        if params is not None:
            list_params.update(params)
        if thin is None:
            thin = self._thin_default
        list_params['thin'] = thin
        results = self.list_resource(resource, search, list_params)
        if resource == 'snapshots':
            # Snapshots API does not do search
            snapshot = []
            for result in results:
                if result['name'] == name:
                    snapshot.append(result)
                    break
            results = snapshot
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
                result = self.show_resource(resource, result['id'], params=params)
        return result

    def find_resource_by_name(self, resource, name, **kwargs):
        search = 'name="{}"'.format(name)
        kwargs['name'] = name
        return self.find_resource(resource, search, **kwargs)

    def find_resource_by_title(self, resource, title, **kwargs):
        search = 'title="{}"'.format(title)
        return self.find_resource(resource, search, **kwargs)

    def find_resources(self, resource, search_list, **kwargs):
        return [self.find_resource(resource, search_item, **kwargs) for search_item in search_list]

    def find_resources_by_name(self, resource, names, **kwargs):
        return [self.find_resource_by_name(resource, name, **kwargs) for name in names]

    def find_resources_by_title(self, resource, titles, **kwargs):
        return [self.find_resource_by_title(resource, title, **kwargs) for title in titles]

    def find_operatingsystem(self, name, params=None, failsafe=False, thin=None):
        result = self.find_resource_by_title('operatingsystems', name, params=params, failsafe=True, thin=thin)
        if not result:
            search = 'title~"{}"'.format(name)
            result = self.find_resource('operatingsystems', search, params=params, failsafe=failsafe, thin=thin)
        return result

    def find_operatingsystems(self, names, **kwargs):
        return [self.find_operatingsystem(name, **kwargs) for name in names]

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
                    volatile_entity[key] = entity_dict[key]
                    fields.append(key)
        if len(fields) > 0:
            new_data = {'id': entity_id}
            for key, value in volatile_entity.items():
                if key in fields:
                    new_data[key] = value
            return self._resource_action(resource, 'update', params=new_data)
        return False, result

    def ensure_resource_state(self, *args, **kwargs):
        changed, _ = self.ensure_resource(*args, **kwargs)
        return changed

    @_exception2fail_json('Failed to ensure entity state: %s')
    def ensure_resource(self, resource, entity_dict, entity, state=None, name_map=None, check_missing=None, check_type=None, force_update=None):
        """ Ensure that a given entity has a certain state """
        if state is None:
            state = self.state
        if name_map is None:
            name_map = self.name_map

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

    def ensure_entity_state(self, *args, **kwargs):
        changed, _ = self.ensure_entity(*args, **kwargs)
        return changed

    @_exception2fail_json('Failed to ensure entity state: %s')
    def ensure_entity(self, resource, desired_entity, current_entity, params=None, state=None, entity_spec=None):
        """Ensure that a given entity has a certain state

            Parameters:
                resource (string): Plural name of the api resource to manipulate
                desired_entity (dict): Desired properties of the entity
                current_entity (dict, None): Current properties of the entity or None if nonexistent
                params (dict): Lookup parameters (i.e. parent_id for nested entities) (optional)
                state (dict): Desired state of the entity (optionally taken from the module)
                entity_spec (dict): Description of the entity structure (optionally taken from module)
            Return value:
                Pair of boolean indicating whether something changed and the new current state if the entity
        """
        if state is None:
            state = self.state
        if entity_spec is None:
            entity_spec = self.entity_spec

        changed = False
        updated_entity = None

        if state == 'present_with_defaults':
            if current_entity is None:
                changed, updated_entity = self._create_entity(resource, desired_entity, params, entity_spec)
        elif state == 'present':
            if current_entity is None:
                changed, updated_entity = self._create_entity(resource, desired_entity, params, entity_spec)
            else:
                changed, updated_entity = self._update_entity(resource, desired_entity, current_entity, params, entity_spec)
        elif state == 'reverted':
            if current_entity is not None:
                changed, updated_entity = self._revert_entity(resource, current_entity, params)
        elif state == 'absent':
            if current_entity is not None:
                changed, updated_entity = self._delete_entity(resource, current_entity, params)
        else:
            self.fail_json(msg='Not a valid state: {}'.format(state))
        return changed, updated_entity

    def _create_entity(self, resource, desired_entity, params, entity_spec):
        """Create entity with given properties

            Parameters:
                resource (string): Plural name of the api resource to manipulate
                desired_entity (dict): Desired properties of the entity
                params (dict): Lookup parameters (i.e. parent_id for nested entities) (optional)
                entity_spec (dict): Description of the entity structure
            Return value:
                Pair of boolean indicating whether something changed and the new current state if the entity
        """
        payload = _flatten_entity(desired_entity, entity_spec)
        if params:
            payload.update(params)
        return self._resource_action(resource, 'create', payload)

    def _update_entity(self, resource, desired_entity, current_entity, params, entity_spec):
        """Update a given entity with given properties if any diverge

            Parameters:
                resource (string): Plural name of the api resource to manipulate
                desired_entity (dict): Desired properties of the entity
                current_entity (dict): Current properties of the entity
                params (dict): Lookup parameters (i.e. parent_id for nested entities) (optional)
                entity_spec (dict): Description of the entity structure
            Return value:
                Pair of boolean indicating whether something changed and the new current state if the entity
        """
        payload = {}
        desired_entity = _flatten_entity(desired_entity, entity_spec)
        current_entity = _flatten_entity(current_entity, entity_spec)
        for key, value in desired_entity.items():
            if current_entity.get(key) == value:
                continue
            payload[key] = value
        if payload:
            payload['id'] = current_entity['id']
            if params:
                payload.update(params)
            return self._resource_action(resource, 'update', payload)
        else:
            return False, current_entity

    def _revert_entity(self, resource, current_entity, params):
        """Revert a given entity

            Parameters:
                resource (string): Plural name of the api resource to manipulate
                current_entity (dict): Current properties of the entity
                params (dict): Lookup parameters (i.e. parent_id for nested entities) (optional)
            Return value:
                Pair of boolean indicating whether something changed and the new current state of the entity
        """
        payload = {'id': current_entity['id']}
        if params:
            payload.update(params)
        return self._resource_action(resource, 'revert', payload)

    def _delete_entity(self, resource, current_entity, params):
        """Delete a given entity

            Parameters:
                resource (string): Plural name of the api resource to manipulate
                current_entity (dict): Current properties of the entity
                params (dict): Lookup parameters (i.e. parent_id for nested entities) (optional)
            Return value:
                Pair of boolean indicating whether something changed and the new current state of the entity
        """
        payload = {'id': current_entity['id']}
        if params:
            payload.update(params)
        return self._resource_action(resource, 'destroy', payload)

    def _resource_action(self, resource, action, params):
        resource_payload = self.foremanapi.resource(resource).action(action).prepare_params(params)
        try:
            result = None
            if not self.check_mode:
                result = self.foremanapi.resource(resource).call(action, resource_payload)
        except Exception as e:
            self.fail_json(msg='Error while performing {} on {}: {}'.format(
                action, resource, str(e)))
        return True, result

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

        self.state = self.params.pop('state')
        self.desired_absent = self.state == 'absent'

    def parse_params(self):
        return (super(ForemanEntityAnsibleModule, self).parse_params(), self.state)


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
        name_map = kwargs.pop('name_map', {})
        entity_spec = kwargs.pop('entity_spec', {})
        super(ForemanEntityApypieAnsibleModule, self).__init__(argument_spec=args, **kwargs)

        self.entity_spec = entity_spec
        self.name_map = name_map
        self.state = self.params.pop('state')
        self.desired_absent = self.state == 'absent'
        self._thin_default = self.desired_absent

    def parse_params(self):
        return (super(ForemanEntityApypieAnsibleModule, self).parse_params(), self.state)


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


def _flatten_entity(entity, entity_spec):
    """Flatten entity according to spec"""
    result = {}
    for key, value in entity.items():
        if key in entity_spec:
            spec = entity_spec[key]
            flat_name = spec.get('flat_name', key)
            property_type = spec.get('type', 'str')
            if property_type == 'entity':
                result[flat_name] = value['id']
            elif property_type == 'entity_list':
                result[flat_name] = sorted(val['id'] for val in value)
            else:
                result[flat_name] = value
    return result


# Helper for (global, operatingsystem, ...) parameters
def parameter_value_to_str(value, parameter_type):
    """Helper to convert the value of parameters to string according to their parameter_type."""
    if parameter_type in ['real']:
        parameter_string = str(value)
    elif parameter_type in ['array', 'hash', 'yaml', 'json']:
        parameter_string = json.dumps(value)
    else:
        parameter_string = value
    return parameter_string


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
    """ Split fully qualified name (title) in name and parent title """
    fqn = title.split('/')
    if len(fqn) > 1:
        name = fqn.pop()
        return (name, '/'.join(fqn))
    else:
        return (title, None)


def build_fqn(name, parent=None):
    if parent:
        return "%s/%s" % (parent, name)
    else:
        return name

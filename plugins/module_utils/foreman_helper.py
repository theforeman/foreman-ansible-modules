# -*- coding: utf-8 -*-
# (c) Matthias Dellweg (ATIX AG) 2017

import json
import re
import time
import traceback
import yaml

from ansible.module_utils.basic import AnsibleModule

try:
    import apypie
    HAS_APYPIE = True
except ImportError:
    HAS_APYPIE = False
    APYPIE_IMP_ERR = traceback.format_exc()


parameter_entity_spec = dict(
    name=dict(required=True),
    value=dict(type='raw', required=True),
    parameter_type=dict(default='string', choices=['string', 'boolean', 'integer', 'real', 'array', 'hash', 'yaml', 'json']),
)


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

        self._params = self.params.copy()

        self.check_requirements()

        self._foremanapi_server_url = self._params.pop('server_url')
        self._foremanapi_username = self._params.pop('username')
        self._foremanapi_password = self._params.pop('password')
        self._foremanapi_validate_certs = self._params.pop('validate_certs')

    def parse_params(self):
        self.warn("Use of deprecated method parse_params")
        return {k: v for (k, v) in self._params.items() if v is not None}

    def clean_params(self):
        return {k: v for (k, v) in self._params.items() if v is not None}

    def get_server_params(self):
        return (self._foremanapi_server_url, self._foremanapi_username, self._foremanapi_password, self._foremanapi_validate_certs)


class KatelloMixin(object):
    def __init__(self, argument_spec=None, **kwargs):
        args = dict(
            organization=dict(required=True),
        )
        if argument_spec:
            args.update(argument_spec)
        super(KatelloMixin, self).__init__(argument_spec=args, **kwargs)

    def connect(self, ping=True):
        super(KatelloMixin, self).connect(ping)
        self._patch_organization_update_api()
        self._patch_subscription_index_api()
        self._patch_subscription_upload_api()
        self._patch_sync_plan_api()

    def _patch_organization_update_api(self):
        """This is a workaround for the broken organization update apidoc in katello.
            see https://projects.theforeman.org/issues/27538
        """

        _organization_methods = self.foremanapi.apidoc['docs']['resources']['organizations']['methods']

        _organization_update = next(x for x in _organization_methods if x['name'] == 'update')
        _organization_update_params_organization = next(x for x in _organization_update['params'] if x['name'] == 'organization')
        _organization_update_params_organization['required'] = False

    def _patch_subscription_index_api(self):
        """This is a workaround for the broken subscriptions apidoc in katello.
        https://projects.theforeman.org/issues/27575
        """

        _subscription_methods = self.foremanapi.apidoc['docs']['resources']['subscriptions']['methods']

        _subscription_index = next(x for x in _subscription_methods if x['name'] == 'index')
        _subscription_index_params_organization_id = next(x for x in _subscription_index['params'] if x['name'] == 'organization_id')
        _subscription_index_params_organization_id['required'] = False

    def _patch_subscription_upload_api(self):
        """This is a workaround for the broken subscription upload apidoc in katello.
            see https://projects.theforeman.org/issues/27527
        """

        _subscription_methods = self.foremanapi.apidoc['docs']['resources']['subscriptions']['methods']

        _subscription_upload = next(x for x in _subscription_methods if x['name'] == 'upload')
        _subscription_upload_params_content = next(x for x in _subscription_upload['params'] if x['name'] == 'content')
        _subscription_upload_params_content['expected_type'] = 'any_type'

    def _patch_sync_plan_api(self):
        """This is a workaround for the broken sync_plan apidoc in katello.
            see https://projects.theforeman.org/issues/27532
        """

        _organization_parameter = {
            u'validations': [],
            u'name': u'organization_id',
            u'show': True,
            u'description': u'\n<p>Filter sync plans by organization name or label</p>\n',
            u'required': False,
            u'allow_nil': False,
            u'allow_blank': False,
            u'full_name': u'organization_id',
            u'expected_type': u'numeric',
            u'metadata': None,
            u'validator': u'Must be a number.',
        }

        _sync_plan_methods = self.foremanapi.apidoc['docs']['resources']['sync_plans']['methods']

        _sync_plan_add_products = next(x for x in _sync_plan_methods if x['name'] == 'add_products')
        if next((x for x in _sync_plan_add_products['params'] if x['name'] == 'organization_id'), None) is None:
            _sync_plan_add_products['params'].append(_organization_parameter)

        _sync_plan_remove_products = next(x for x in _sync_plan_methods if x['name'] == 'remove_products')
        if next((x for x in _sync_plan_remove_products['params'] if x['name'] == 'organization_id'), None) is None:
            _sync_plan_remove_products['params'].append(_organization_parameter)


def _exception2fail_json(msg='Generic failure: %s'):
    def decor(f):
        def inner(self, *args, **kwargs):
            try:
                return f(self, *args, **kwargs)
            except Exception as e:
                self.fail_json(msg=msg % e)
        return inner
    return decor


class ForemanApypieAnsibleModule(ForemanBaseAnsibleModule):

    def __init__(self, *args, **kwargs):
        super(ForemanApypieAnsibleModule, self).__init__(*args, **kwargs)
        self._thin_default = False
        self.state = 'undefined'
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
            self.fail_json(msg='The apypie Python module is required', exception=APYPIE_IMP_ERR)

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
        else:
            entity_spec, _ = _entity_spec_helper(entity_spec)

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
        elif state == 'copied':
            if current_entity is not None:
                changed, updated_entity = self._copy_entity(resource, desired_entity, current_entity, params)
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
        if not self.check_mode:
            if params:
                payload.update(params)
            return self.resource_action(resource, 'create', payload)
        else:
            fake_entity = desired_entity.copy()
            fake_entity['id'] = -1
            return True, fake_entity

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
            if current_entity.get(key) != value:
                payload[key] = value
        if payload:
            payload['id'] = current_entity['id']
            if not self.check_mode:
                if params:
                    payload.update(params)
                return self.resource_action(resource, 'update', payload)
            else:
                # In check_mode we emulate the server updating the entity
                fake_entity = current_entity.copy()
                fake_entity.update(payload)
                return True, fake_entity
        else:
            # Nothing needs changing
            return False, current_entity

    def _copy_entity(self, resource, desired_entity, current_entity, params):
        """Copy a given entity

            Parameters:
                resource (string): Plural name of the api resource to manipulate
                current_entity (dict): Current properties of the entity
                params (dict): Lookup parameters (i.e. parent_id for nested entities) (optional)
            Return value:
                Pair of boolean indicating whether something changed and the new current state of the entity
        """
        payload = {
            'id': current_entity['id'],
            'new_name': desired_entity['new_name'],
        }
        if params:
            payload.update(params)
        return self.resource_action(resource, 'copy', payload)

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
        return self.resource_action(resource, 'revert', payload)

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
        self.resource_action(resource, 'destroy', payload)
        return True, None

    def resource_action(self, resource, action, params, options=None, files=None):
        resource_payload = self.foremanapi.resource(resource).action(action).prepare_params(params)
        if options is None:
            options = {}
        try:
            result = None
            if not self.check_mode:
                result = self.foremanapi.resource(resource).call(action, resource_payload, options=options, files=files)
        except Exception as e:
            self.fail_json(msg='Error while performing {} on {}: {}'.format(
                action, resource, str(e)))
        return True, result

    def wait_for_task(self, task, duration=60, poll=4):
        while task['state'] not in ['paused', 'stopped']:
            duration -= poll
            if duration <= 0:
                self.fail_json(msg="Timout waiting for Task {}".format(task['id']))
            time.sleep(poll)

            _, task = self.resource_action('foreman_tasks', 'show', {'id': task['id']})

        return task


class ForemanEntityApypieAnsibleModule(ForemanApypieAnsibleModule):

    def __init__(self, argument_spec=None, **kwargs):
        entity_spec, gen_args = _entity_spec_helper(kwargs.pop('entity_spec', {}))
        args = dict(
            state=dict(choices=['present', 'absent'], default='present'),
        )
        args.update(gen_args)
        if argument_spec is not None:
            args.update(argument_spec)
        super(ForemanEntityApypieAnsibleModule, self).__init__(argument_spec=args, **kwargs)

        self.entity_spec = entity_spec
        self.state = self._params.pop('state')
        self.desired_absent = self.state == 'absent'
        self._thin_default = self.desired_absent

    def parse_params(self):
        return (super(ForemanEntityApypieAnsibleModule, self).parse_params(), self.state)

    def ensure_scoped_parameters(self, scope, entity, parameters):
        changed = False
        if parameters is not None:
            if self.state == 'present' or (self.state == 'present_with_defaults' and entity is None):
                if entity:
                    current_parameters = {parameter['name']: parameter for parameter in self.list_resource('parameters', params=scope)}
                else:
                    current_parameters = {}
                desired_parameters = {parameter['name']: parameter for parameter in parameters}

                for name in desired_parameters:
                    desired_parameter = desired_parameters[name]
                    desired_parameter['value'] = parameter_value_to_str(desired_parameter['value'], desired_parameter['parameter_type'])
                    current_parameter = current_parameters.pop(name, None)
                    if current_parameter:
                        if 'parameter_type' not in current_parameter:
                            current_parameter['parameter_type'] = 'string'
                        current_parameter['value'] = parameter_value_to_str(current_parameter['value'], current_parameter['parameter_type'])
                    changed |= self.ensure_entity_state(
                        'parameters', desired_parameter, current_parameter, state="present", entity_spec=parameter_entity_spec, params=scope)
                for current_parameter in current_parameters.values():
                    changed |= self.ensure_entity_state(
                        'parameters', None, current_parameter, state="absent", entity_spec=parameter_entity_spec, params=scope)
        return changed


class KatelloEntityApypieAnsibleModule(KatelloMixin, ForemanEntityApypieAnsibleModule):
    pass


def _entity_spec_helper(spec):
    """Extend an entity spec by adding entries for all flat_names.
    Extract ansible compatible argument_spec on the way.
    """
    entity_spec = {'id': {}}
    argument_spec = {}
    for key, value in spec.items():
        entity_value = {}
        argument_value = value.copy()
        if 'flat_name' in argument_value:
            flat_name = argument_value.pop('flat_name')
            entity_value['flat_name'] = flat_name
            entity_spec[flat_name] = {}

        if argument_value.get('type') == 'entity':
            entity_value['type'] = argument_value.pop('type')
        elif argument_value.get('type') == 'entity_list':
            argument_value['type'] = 'list'
            entity_value['type'] = 'entity_list'
        elif argument_value.get('type') == 'nested_list':
            argument_value['type'] = 'list'
            argument_value['elements'] = 'dict'
            _, argument_value['options'] = _entity_spec_helper(argument_value.pop('entity_spec'))
            entity_value = None
        if entity_value is not None:
            entity_spec[key] = entity_value
        if argument_value.get('type') != 'invisible':
            argument_spec[key] = argument_value

    return entity_spec, argument_spec


def _flatten_entity(entity, entity_spec):
    """Flatten entity according to spec"""
    result = {}
    for key, value in entity.items():
        if key in entity_spec and value is not None:
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
    if parameter_type in ['real', 'integer']:
        parameter_string = str(value)
    elif parameter_type in ['array', 'hash', 'yaml', 'json']:
        parameter_string = json.dumps(value, sort_keys=True)
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

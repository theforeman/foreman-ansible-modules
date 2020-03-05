# -*- coding: utf-8 -*-
# (c) Matthias Dellweg (ATIX AG) 2017

from __future__ import absolute_import, division, print_function
__metaclass__ = type


import json
import re
import time
import traceback

from contextlib import contextmanager

from collections import defaultdict
from functools import wraps

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_bytes, to_native
from ansible.module_utils import six

try:
    import apypie
    import requests.exceptions
    HAS_APYPIE = True
except ImportError:
    HAS_APYPIE = False
    APYPIE_IMP_ERR = traceback.format_exc()

try:
    import yaml
    HAS_PYYAML = True
except ImportError:
    HAS_PYYAML = False
    PYYAML_IMP_ERR = traceback.format_exc()

parameter_foreman_spec = dict(
    name=dict(required=True),
    value=dict(type='raw', required=True),
    parameter_type=dict(default='string', choices=['string', 'boolean', 'integer', 'real', 'array', 'hash', 'yaml', 'json']),
)


def _exception2fail_json(msg='Generic failure: {0}'):
    def decor(f):
        @wraps(f)
        def inner(self, *args, **kwargs):
            try:
                return f(self, *args, **kwargs)
            except Exception as e:
                self.fail_from_exception(e, msg.format(to_native(e)))
        return inner
    return decor


class OrganizationMixin(object):
    def handle_organization_param(self, entity_dict):
        """
        Find the Organization referenced in the entity_dict.
        This *always* executes the search as we also need to know the Organization when deleting entities.

        Parameters:
            entity_dict (dict): the entity data as entered by the user
        Return value:
            entity_dict (dict): updated data
            scope (dict): params that can be passed to further API calls to scope for the Organization
        """
        entity_dict = entity_dict.copy()

        entity_dict['organization'] = self.find_resource_by_name('organizations', name=entity_dict['organization'], thin=True)

        scope = {'organization_id': entity_dict['organization']['id']}

        return (entity_dict, scope)


class KatelloMixin(OrganizationMixin):
    @_exception2fail_json(msg="Failed to connect to Foreman server: {0}")
    def connect(self):
        super(KatelloMixin, self).connect()

        if 'subscriptions' not in self.foremanapi.resources:
            raise Exception('The server does not seem to have the Katello plugin installed.')

        self._patch_content_uploads_update_api()
        self._patch_organization_update_api()
        self._patch_subscription_index_api()
        self._patch_sync_plan_api()

    def _patch_content_uploads_update_api(self):
        """This is a workaround for the broken content_uploads update apidoc in katello.
            see https://projects.theforeman.org/issues/27590
        """

        _content_upload_methods = self.foremanapi.apidoc['docs']['resources']['content_uploads']['methods']

        _content_upload_update = next(x for x in _content_upload_methods if x['name'] == 'update')
        _content_upload_update_params_id = next(x for x in _content_upload_update['params'] if x['name'] == 'id')
        _content_upload_update_params_id['expected_type'] = 'string'

        _content_upload_destroy = next(x for x in _content_upload_methods if x['name'] == 'destroy')
        _content_upload_destroy_params_id = next(x for x in _content_upload_destroy['params'] if x['name'] == 'id')
        _content_upload_destroy_params_id['expected_type'] = 'string'

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


class HostMixin(object):
    def __init__(self, foreman_spec=None, **kwargs):
        args = dict(
            compute_resource=dict(type='entity'),
            compute_profile=dict(type='entity'),
            domain=dict(type='entity'),
            subnet=dict(type='entity'),
            subnet6=dict(type='entity', resource_type='subnets'),
            parameters=dict(type='nested_list', foreman_spec=parameter_foreman_spec),
            root_pass=dict(no_log=True),
        )
        if foreman_spec:
            args.update(foreman_spec)
        super(HostMixin, self).__init__(foreman_spec=args, **kwargs)


class ForemanAnsibleModule(AnsibleModule):

    def __init__(self, argument_spec=None, **kwargs):
        # State recording for changed and diff reporting
        self._changed = False
        self._before = defaultdict(list)
        self._after = defaultdict(list)
        self._after_full = defaultdict(list)

        self.original_foreman_spec = kwargs.pop('foreman_spec', {})
        foreman_spec, gen_args = _foreman_spec_helper(self.original_foreman_spec)
        self.foreman_spec = foreman_spec
        args = dict(
            server_url=dict(required=True),
            username=dict(required=True),
            password=dict(required=True, no_log=True),
            validate_certs=dict(type='bool', default=True, aliases=['verify_ssl']),
        )
        if argument_spec is not None:
            args.update(argument_spec)
        args.update(gen_args)
        supports_check_mode = kwargs.pop('supports_check_mode', True)
        self._aliases = {alias for arg in args.values() for alias in arg.get('aliases', [])}
        super(ForemanAnsibleModule, self).__init__(argument_spec=args, supports_check_mode=supports_check_mode, **kwargs)

        self._params = self.params.copy()

        self.check_requirements()

        self._foremanapi_server_url = self._params.pop('server_url')
        self._foremanapi_username = self._params.pop('username')
        self._foremanapi_password = self._params.pop('password')
        self._foremanapi_validate_certs = self._params.pop('validate_certs')
        if 'verify_ssl' in self._params:
            self.warn("Please use 'validate_certs' instead of deprecated 'verify_ssl'.")

        self.task_timeout = 60
        self.task_poll = 4

        self._thin_default = False
        self.state = 'undefined'

    @contextmanager
    def api_connection(self):
        self.connect()
        yield
        self.exit_json()

    @property
    def changed(self):
        return self._changed

    def set_changed(self):
        self._changed = True

    def clean_params(self):
        return {k: v for (k, v) in self._params.items() if v is not None and k not in self._aliases}

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

    def _patch_subnet_rex_api(self):
        """This is a workaround for the broken subnet apidoc in foreman remote execution.
            see https://projects.theforeman.org/issues/19086
        """

        if 'remote_execution_features' not in self.foremanapi.apidoc['docs']['resources']:
            # the system has no foreman_remote_execution installed, no need to patch
            return

        _subnet_rex_proxies_parameter = {
            u'validations': [],
            u'name': u'remote_execution_proxy_ids',
            u'show': True,
            u'description': u'\n<p>Remote Execution Proxy IDs</p>\n',
            u'required': False,
            u'allow_nil': True,
            u'allow_blank': False,
            u'full_name': u'subnet[remote_execution_proxy_ids]',
            u'expected_type': u'array',
            u'metadata': None,
            u'validator': u'',
        }
        _subnet_methods = self.foremanapi.apidoc['docs']['resources']['subnets']['methods']

        _subnet_create = next(x for x in _subnet_methods if x['name'] == 'create')
        _subnet_create_params_subnet = next(x for x in _subnet_create['params'] if x['name'] == 'subnet')
        _subnet_create_params_subnet['params'].append(_subnet_rex_proxies_parameter)

        _subnet_update = next(x for x in _subnet_methods if x['name'] == 'update')
        _subnet_update_params_subnet = next(x for x in _subnet_update['params'] if x['name'] == 'subnet')
        _subnet_update_params_subnet['params'].append(_subnet_rex_proxies_parameter)

    def check_requirements(self):
        if not HAS_APYPIE:
            self.fail_json(msg='The apypie Python module is required', exception=APYPIE_IMP_ERR)

    @_exception2fail_json(msg="Failed to connect to Foreman server: {0}")
    def connect(self):
        self.foremanapi = apypie.Api(
            uri=self._foremanapi_server_url,
            username=to_bytes(self._foremanapi_username),
            password=to_bytes(self._foremanapi_password),
            api_version=2,
            verify_ssl=self._foremanapi_validate_certs,
        )

        self.ping()

        self._patch_location_api()
        self._patch_subnet_rex_api()

    @_exception2fail_json(msg="Failed to connect to Foreman server: {0}")
    def ping(self):
        return self.foremanapi.resource('home').call('status')

    def _resource(self, resource):
        if resource not in self.foremanapi.resources:
            raise Exception("The server doesn't know about {0}, is the right plugin installed?".format(resource))
        return self.foremanapi.resource(resource)

    def _resource_call(self, resource, *args, **kwargs):
        return self._resource(resource).call(*args, **kwargs)

    def _resource_prepare_params(self, resource, action, params):
        return self._resource(resource).action(action).prepare_params(params)

    @_exception2fail_json(msg='Failed to show resource: {0}')
    def show_resource(self, resource, resource_id, params=None):
        if params is None:
            params = {}
        else:
            params = params.copy()

        params['id'] = resource_id

        params = self._resource_prepare_params(resource, 'show', params)

        return self._resource_call(resource, 'show', params)

    @_exception2fail_json(msg='Failed to list resource: {0}')
    def list_resource(self, resource, search=None, params=None):
        if params is None:
            params = {}
        else:
            params = params.copy()

        if search is not None:
            params['search'] = search
        params['per_page'] = 2 << 31

        params = self._resource_prepare_params(resource, 'index', params)

        return self._resource_call(resource, 'index', params)['results']

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
            if len(results) > 1:
                error_msg = "too many ({0})".format(len(results))
            else:
                error_msg = "no"
            self.fail_json(msg="Found {0} results while searching for {1} with {2}".format(error_msg, resource, search))
        if result:
            if thin:
                result = {'id': result['id']}
            else:
                result = self.show_resource(resource, result['id'], params=params)
        return result

    def find_resource_by(self, resource, search_field, value, **kwargs):
        search = '{0}{1}"{2}"'.format(search_field, kwargs.pop('search_operator', '='), value)
        if search_field == 'name':
            kwargs['name'] = value
        return self.find_resource(resource, search, **kwargs)

    def find_resource_by_name(self, resource, name, **kwargs):
        return self.find_resource_by(resource, 'name', name, **kwargs)

    def find_resource_by_title(self, resource, title, **kwargs):
        return self.find_resource_by(resource, 'title', title, **kwargs)

    def find_resource_by_id(self, resource, obj_id, **kwargs):
        return self.find_resource_by(resource, 'id', obj_id, **kwargs)

    def find_resources_by(self, resource, search_field, search_list, **kwargs):
        return [self.find_resource_by(resource, search_field, search_item, **kwargs) for search_item in search_list]

    def find_resources_by_name(self, resource, names, **kwargs):
        return [self.find_resource_by_name(resource, name, **kwargs) for name in names]

    def find_resources_by_title(self, resource, titles, **kwargs):
        return [self.find_resource_by_title(resource, title, **kwargs) for title in titles]

    def find_resources_by_id(self, resource, obj_ids, **kwargs):
        return [self.find_resource_by_id(resource, obj_id, **kwargs) for obj_id in obj_ids]

    def find_operatingsystem(self, name, params=None, failsafe=False, thin=None):
        result = self.find_resource_by_title('operatingsystems', name, params=params, failsafe=True, thin=thin)
        if not result:
            result = self.find_resource_by('operatingsystems', 'title', name, search_operator='~', params=params, failsafe=failsafe, thin=thin)
        return result

    def find_operatingsystems(self, names, **kwargs):
        return [self.find_operatingsystem(name, **kwargs) for name in names]

    def find_puppetclass(self, name, environment=None, params=None, failsafe=False, thin=None):
        if environment:
            scope = {'environment_id': environment}
        else:
            scope = None
        search = 'name="{0}"'.format(name)
        results = self.list_resource('puppetclasses', search, params=scope)

        # verify that only one puppet module is returned with only one puppet class inside
        # as provided search results have to be like "results": { "ntp": [{"id": 1, "name": "ntp" ...}]}
        # and get the puppet class id
        if len(results) == 1 and len(list(results.values())[0]) == 1:
            result = list(results.values())[0][0]
            if thin:
                return {'id': result['id']}
            else:
                return result

        if failsafe:
            return None
        else:
            self.fail_json(msg='No data found for name="%s"' % search)

    def find_puppetclasses(self, names, **kwargs):
        return [self.find_puppetclass(name, **kwargs) for name in names]

    def record_before(self, resource, entity):
        self._before[resource].append(entity)

    def record_after(self, resource, entity):
        self._after[resource].append(entity)

    def record_after_full(self, resource, entity):
        self._after_full[resource].append(entity)

    @_exception2fail_json(msg='Failed to ensure entity state: {0}')
    def ensure_entity(self, resource, desired_entity, current_entity, params=None, state=None, foreman_spec=None):
        """Ensure that a given entity has a certain state

            Parameters:
                resource (string): Plural name of the api resource to manipulate
                desired_entity (dict): Desired properties of the entity
                current_entity (dict, None): Current properties of the entity or None if nonexistent
                params (dict): Lookup parameters (i.e. parent_id for nested entities) (optional)
                state (dict): Desired state of the entity (optionally taken from the module)
                foreman_spec (dict): Description of the entity structure (optionally taken from module)
            Return value:
                The new current state of the entity
        """
        if state is None:
            state = self.state
        if foreman_spec is None:
            foreman_spec = self.foreman_spec
        else:
            foreman_spec, _dummy = _foreman_spec_helper(foreman_spec)

        updated_entity = None

        self.record_before(resource, _flatten_entity(current_entity, foreman_spec))

        if state == 'present_with_defaults':
            if current_entity is None:
                updated_entity = self._create_entity(resource, desired_entity, params, foreman_spec)
        elif state == 'present':
            if current_entity is None:
                updated_entity = self._create_entity(resource, desired_entity, params, foreman_spec)
            else:
                updated_entity = self._update_entity(resource, desired_entity, current_entity, params, foreman_spec)
        elif state == 'copied':
            if current_entity is not None:
                updated_entity = self._copy_entity(resource, desired_entity, current_entity, params)
        elif state == 'reverted':
            if current_entity is not None:
                updated_entity = self._revert_entity(resource, current_entity, params)
        elif state == 'absent':
            if current_entity is not None:
                updated_entity = self._delete_entity(resource, current_entity, params)
        else:
            self.fail_json(msg='Not a valid state: {0}'.format(state))

        self.record_after(resource, _flatten_entity(updated_entity, foreman_spec))
        self.record_after_full(resource, updated_entity)

        return updated_entity

    def _create_entity(self, resource, desired_entity, params, foreman_spec):
        """Create entity with given properties

            Parameters:
                resource (string): Plural name of the api resource to manipulate
                desired_entity (dict): Desired properties of the entity
                params (dict): Lookup parameters (i.e. parent_id for nested entities) (optional)
                foreman_spec (dict): Description of the entity structure
            Return value:
                The new current state if the entity
        """
        payload = _flatten_entity(desired_entity, foreman_spec)
        if not self.check_mode:
            if params:
                payload.update(params)
            return self.resource_action(resource, 'create', payload)
        else:
            fake_entity = desired_entity.copy()
            fake_entity['id'] = -1
            self.set_changed()
            return fake_entity

    def _update_entity(self, resource, desired_entity, current_entity, params, foreman_spec):
        """Update a given entity with given properties if any diverge

            Parameters:
                resource (string): Plural name of the api resource to manipulate
                desired_entity (dict): Desired properties of the entity
                current_entity (dict): Current properties of the entity
                params (dict): Lookup parameters (i.e. parent_id for nested entities) (optional)
                foreman_spec (dict): Description of the entity structure
            Return value:
                The new current state if the entity
        """
        payload = {}
        desired_entity = _flatten_entity(desired_entity, foreman_spec)
        current_entity = _flatten_entity(current_entity, foreman_spec)
        for key, value in desired_entity.items():
            # String comparison needs extra care in face of unicode
            if foreman_spec[key].get('type', 'str') == 'str':
                if to_native(current_entity.get(key)) != to_native(value):
                    payload[key] = value
            else:
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
                self.set_changed()
                return fake_entity
        else:
            # Nothing needs changing
            return current_entity

    def _copy_entity(self, resource, desired_entity, current_entity, params):
        """Copy a given entity

            Parameters:
                resource (string): Plural name of the api resource to manipulate
                current_entity (dict): Current properties of the entity
                params (dict): Lookup parameters (i.e. parent_id for nested entities) (optional)
            Return value:
                The new current state of the entity
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
                The new current state of the entity
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
                The new current state of the entity
        """
        payload = {'id': current_entity['id']}
        if params:
            payload.update(params)
        entity = self.resource_action(resource, 'destroy', payload)

        # this is a workaround for https://projects.theforeman.org/issues/26937
        if entity and 'error' in entity and 'message' in entity['error']:
            self.fail_json(msg=entity['error']['message'])

        return None

    def resource_action(self, resource, action, params, options=None, data=None, files=None,
                        ignore_check_mode=False, record_change=True, ignore_task_errors=False):
        resource_payload = self._resource_prepare_params(resource, action, params)
        if options is None:
            options = {}
        try:
            result = None
            if ignore_check_mode or not self.check_mode:
                result = self._resource_call(resource, action, resource_payload, options=options, data=data, files=files)
                is_foreman_task = isinstance(result, dict) and 'action' in result and 'state' in result and 'started_at' in result
                if is_foreman_task:
                    result = self.wait_for_task(result, ignore_errors=ignore_task_errors)
        except Exception as e:
            msg = 'Error while performing {0} on {1}: {2}'.format(
                action, resource, to_native(e))
            self.fail_from_exception(e, msg)
        if record_change and not ignore_check_mode:
            # If we were supposed to ignore check_mode we can assume this action was not a changing one.
            self.set_changed()
        return result

    def wait_for_task(self, task, ignore_errors=False):
        duration = self.task_timeout
        while task['state'] not in ['paused', 'stopped']:
            duration -= self.task_poll
            if duration <= 0:
                self.fail_json(msg="Timout waiting for Task {0}".format(task['id']))
            time.sleep(self.task_poll)

            resource_payload = self._resource_prepare_params('foreman_tasks', 'show', {'id': task['id']})
            task = self._resource_call('foreman_tasks', 'show', resource_payload)
        if not ignore_errors and task['result'] != 'success':
            self.fail_json(msg='Task {0}({1}) did not succeed. Task information: {2}'.format(task['action'], task['id'], task['humanized']['errors']))
        return task

    def fail_from_exception(self, exc, msg):
        fail = {'msg': msg}
        if isinstance(exc, requests.exceptions.HTTPError):
            try:
                response = exc.response.json()
                if 'error' in response:
                    fail['error'] = response['error']
                else:
                    fail['error'] = response
            except Exception:
                fail['error'] = exc.response.text
        self.fail_json(**fail)

    def exit_json(self, changed=False, **kwargs):
        kwargs['changed'] = changed or self.changed
        super(ForemanAnsibleModule, self).exit_json(**kwargs)


class ForemanEntityAnsibleModule(ForemanAnsibleModule):
    """ Base class for Foreman entities. To use it, subclass it with the following convention:
        To manage my_entity entity, create the following sub class:

        ```
        class ForemanMyEntityEntity(ForemanEntityAnsibleModule):
            pass
        ```

        and use that class to instanciate module:

        ```
        module = ForemanMyEntityEntity(
            argument_spec=dict(
                [...]
            ),
            foreman_spec=dict(
                [...]
            ),
        )
        ```

        This add automatic entities resolution based on provided attributes/ sub entities options.
        It add following options to foreman_spec 'entity' and 'entity_list' types:
        * search_by (str): Field used to search the sub entity. Defaults to 'name' unless `parent` was set, in which case it defaults to `title`.
        * search_operator (str): Operator used to search the sub entity. Defaults to '='. For fuzzy search use '~'.
        * resource_type (str): Resource type used to build API resource PATH. Defaults to pluralized entity key.
        * resolve (boolean): Defaults to 'True'. If set to false, the sub entity will not be resolved automatically
        * ensure (boolean): Defaults to 'True'. If set to false, it will be removed before sending data to the foreman server.
        It add following attributes:
        * entity_search (str): Defautls to None. If provided, the base entity resolver will use this search query instead to try to build it.
        * entity_key (str): field used to search current entity. Defaults to value provided by `ENTITY_KEYS` or 'name' if no value found.
        * entity_name (str): name of the current entity.
          By default deduce the entity name from the class name (eg: 'ForemanProvisioningTemplateModule' class will produce 'provisioning_template').
        * entity_scope (str): Type of the entity used to build search scope. Defaults to None.
        * entity_resolve (boolean): Set it to False to disable base entity resolution.
        * entity_opts (dict): Dict of options for base entity. Same options can be provided for subentities described in foreman_spec.
    """

    ENTITY_KEYS = dict(
        hostgroups='title',
        locations='title',
        operatingsystems='title',
        # TODO: Organizations should be search by title (as foreman allow nested orgs) but that's not the case ATM.
        #       Applying this will need to record a lot of tests that is out of scope for the moment.
        # organizations='title',
        users='login',
    )

    @classmethod
    def resolve_entity_key(cls, entity_resource_name):
        """Return field name to search on for provided entity name"""
        if entity_resource_name in cls.ENTITY_KEYS:
            return cls.ENTITY_KEYS[entity_resource_name]
        else:
            return 'name'

    def __init__(self, argument_spec=None, **kwargs):
        self.entity_key = kwargs.pop('entity_key', 'name')
        self.entity_scope = kwargs.pop('entity_scope', None)
        self.entity_resolve = kwargs.pop('entity_resolve', True)
        self.entity_opts = kwargs.pop('entity_opts', {})
        self.entity_name = kwargs.pop('entity_name', self.entity_name_from_class)

        args = dict(
            state=dict(choices=['present', 'absent'], default='present'),
        )
        if argument_spec is not None:
            args.update(argument_spec)
        super(ForemanEntityAnsibleModule, self).__init__(argument_spec=args, **kwargs)

        self.inflector = apypie.Inflector()
        self._entity_resource_name = self.inflector.pluralize(self.entity_name)
        self.state = self._params.pop('state')
        self.desired_absent = self.state == 'absent'
        self._thin_default = self.desired_absent
        self.sub_entities = {key: value for key, value in self.original_foreman_spec.items()
                             if value.get('resolve', True) and value.get('type') in ['entity', 'entity_list']}
        if 'thin' not in self.entity_opts:
            self.entity_opts['thin'] = False
        if 'failsafe' not in self.entity_opts:
            self.entity_opts['failsafe'] = True
        if 'search_operator' not in self.entity_opts:
            self.entity_opts['search_operator'] = '='
        if 'search_by' not in self.entity_opts:
            self.entity_opts['search_by'] = self.resolve_entity_key(self._entity_resource_name)

    @property
    def entity_name_from_class(self):
        """ Convert class name to entity name. The class name must follow folowing name convention:
            * Starts with Foreman or Katello
            * Ends with Module

            This will concert ForemanMyEntityModule class name to my_entity entity name.
            eg:
            * ForemanArchitectureModule => architecture
            * ForemanProvisioningTemplateModule => provisioning_template
            * KatelloProductMudule => product
            * ...
        """
        # Convert current class name from CamelCase to snake_case
        class_name = re.sub(r'(?<=[a-z])[A-Z]|[A-Z](?=[^A-Z])', r'_\g<0>', self.__class__.__name__).lower().strip('_')
        # Get entity name from snake case class name
        return '_'.join(class_name.split('_')[1:-1])

    def run(self, entity_dict=None, entity=None, search=None):
        """ get entity_dict, resolve entities, ensure entity, remove sensitive data, manage parameters.
            You can provide custom entity_dict and entity if custom workflow is needed before doing most of listed actions.
            Returns entity.
        """
        if not entity_dict:
            entity_dict = self.clean_params()

        entity, entity_dict = self.resolve_entities(entity_dict, entity, search)
        new_entity = self.ensure_entity(self._entity_resource_name, self._cleanup_entity_dict(entity_dict), entity)
        new_entity = self.remove_sensitive_fields(new_entity)

        if new_entity:
            self.ensure_entity_parameters(new_entity, entity, entity_dict)

        return new_entity

    def remove_sensitive_fields(self, entity):
        """ Set fields with 'no_log' option to None """
        if entity:
            for blacklisted_field in self.blacklisted_fields:
                entity[blacklisted_field] = None
        return entity

    def ensure_entity_parameters(self, new_entity, entity, entity_dict):
        if ('parameters' in self.original_foreman_spec
           and self.original_foreman_spec['parameters'].get('type', 'str') == 'nested_list' and 'parameters' in entity_dict):
            scope = {'{0}_id'.format(self.entity_name): new_entity['id']}
            self.ensure_scoped_parameters(scope, entity, entity_dict.get('parameters'))

    def resolve_entities(self, entity_dict=None, entity=None, search=None):
        """ This get current entity and all sub entities based on foreman_spec when the param type is 'entity' or 'entity_list'
             and resource_type is defined. You can also pass 'failsafe' and 'thin' options via foreman_spec.
             Params available for subentities:
               * resolve (boolean): True by default. If false, this entity will be excluded and not resolved.
               * failsafe (boolean): False by default.
               * thin (boolean): True by default.
               * scope (str): None by default. Provide the scope of the resource (eg: 'organization') (TODO: manage array for 'nested' scope ?)
                              Defined scope must be a key of foreman_spec.
        """
        if not entity_dict:
            entity_dict = self.clean_params()

        self.entity_opts['thin'] = self.desired_absent

        if not entity and self.entity_resolve:
            if search:
                entity = self.find_resource(self._entity_resource_name, search,
                                            failsafe=self.entity_opts['failsafe'],
                                            thin=self.entity_opts['thin'])
            else:
                entity = self.resolve_base_entity(entity_dict)

        if not self.desired_absent:
            self._resolve_sub_entities(entity, self._unscoped_sub_entities, entity_dict)
            self._resolve_sub_entities(entity, self._scoped_sub_entities, entity_dict)

            updated_key = "updated_" + self.entity_key
            if entity and updated_key in entity_dict:
                entity_dict[self.entity_key] = entity_dict.pop(updated_key)

        return (entity, entity_dict)

    def resolve_base_entity(self, entity_dict):
        entity = None
        if 'parent' in self.sub_entities:
            current, parent = split_fqn(entity_dict[self.entity_key])
            entity_dict[self.entity_key] = current
            if 'parent' in entity_dict and isinstance(entity_dict['parent'], six.string_types):
                if parent:
                    self.fail_json(msg="Please specify the parent either separately, or as part of the title.")
                parent = entity_dict['parent']

            if parent:
                entity_dict['parent'] = self.find_resource_by_title(self._entity_resource_name,
                                                                    parent, thin=True, failsafe=self.desired_absent)
                if self.desired_absent and entity_dict['parent'] is None:
                    # Parent does not exist so just exit here
                    return entity

            value = build_fqn(entity_dict[self.entity_key], parent)
        else:
            value = entity_dict[self.entity_key]
        # Get current entity with its scope if defined (eg: organization for katello resources)
        if self.entity_scope and self.entity_scope in entity_dict:
            if isinstance(entity_dict[self.entity_scope], six.string_types) and self.entity_scope in self._unscoped_sub_entities:
                entity_dict[self.entity_scope] = self._resolve_entity(self.entity_scope, entity_dict[self.entity_scope],
                                                                      self._unscoped_sub_entities[self.entity_scope],
                                                                      params={'failsafe': self.desired_absent})
            if entity_dict[self.entity_scope]:
                if isinstance(entity_dict[self.entity_scope], dict) and 'id' in entity_dict[self.entity_scope]:
                    scope_id = entity_dict[self.entity_scope]['id']
                else:
                    scope_id = entity_dict[self.entity_scope]
                scope = {'{0}_id'.format(self.entity_scope): scope_id}
                entity = self._resolve_entity(self.entity_name, value, entity_opts=self.entity_opts, params=scope)
            else:
                self.fail_json(msg='Scope {0} not found for {1}'.format(to_native(self.entity_scope), self.entity_name))
        elif not self.entity_scope:
            entity = self._resolve_entity(self.entity_name, value, entity_opts=self.entity_opts)
        else:
            self.fail_json(msg='Invalid scope {0} for {1}'.format(to_native(self.entity_scope), self.entity_name))

        return entity

    def _resolve_sub_entities(self, entity, entities, entity_dict):
        for entity_name, entity_opts in {key: value for key, value in entities.items() if key in entity_dict}.items():
            if 'scope' in entity_opts:
                if entity_opts['scope'] == self.entity_name and entity:
                    scope_id = entity['id']
                elif entity_opts['scope'] in entity_dict:
                    scope_id = entity_dict[entity_opts['scope']]['id']

                scope = {'{0}_id'.format(entity_opts['scope']): scope_id}
            else:
                scope = None
            if entity_opts['type'] == 'entity' and isinstance(entity_dict[entity_name], six.string_types):
                entity_dict[entity_name] = self._resolve_entity(entity_name, entity_dict[entity_name], entity_opts, params=scope)
            elif (entity_opts['type'] == 'entity_list' and isinstance(entity_dict[entity_name], list)
                  and len(entity_dict[entity_name]) > 0 and isinstance(entity_dict[entity_name][0], six.string_types)):
                entity_dict[entity_name] = self._resolve_entity_list(entity_name, entity_dict[entity_name], entity_opts, params=scope)

    @property
    def _unscoped_sub_entities(self):
        return {key: value for key, value in self.sub_entities.items() if 'scope' not in value}

    @property
    def _scoped_sub_entities(self):
        return {key: value for key, value in self.sub_entities.items() if 'scope' in value}

    def _cleanup_entity_dict(self, entity_dict):
        for key, value in self.original_foreman_spec.items():
            if not value.get('ensure', True) and key in entity_dict:
                entity_dict.pop(key)
        return entity_dict

    def _resolve_entity(self, entity_name, value, entity_opts, params=None):
        resource_path = entity_opts.get('resource_type', self.inflector.pluralize(entity_name))
        failsafe = entity_opts.get('failsafe', False)
        thin = entity_opts.get('thin', True)
        if resource_path == 'operatingsystems':
            return self.find_operatingsystem(value, params=params, failsafe=failsafe, thin=thin)
        elif resource_path == 'puppetclasses':
            return self.find_puppetclass(value, params=params, failsafe=failsafe, thin=thin)
        else:
            return self.find_resource_by(resource_path,
                                         entity_opts.get('search_by', self.__class__.resolve_entity_key(resource_path)), value,
                                         search_operator=entity_opts.get('search_operator', '='),
                                         failsafe=failsafe, thin=thin, params=params)

    def _resolve_entity_list(self, entity_name, values, entity_opts, params=None):
        opts = entity_opts.copy()
        opts['resource_type'] = entity_opts.get('resource_type', entity_name)
        return [self._resolve_entity(entity_name, value, opts, params) for value in values]

    def ensure_scoped_parameters(self, scope, entity, parameters):
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
                    self.ensure_entity(
                        'parameters', desired_parameter, current_parameter, state="present", foreman_spec=parameter_foreman_spec, params=scope)
                for current_parameter in current_parameters.values():
                    self.ensure_entity(
                        'parameters', None, current_parameter, state="absent", foreman_spec=parameter_foreman_spec, params=scope)

    def exit_json(self, **kwargs):
        if 'diff' not in kwargs and (self._before or self._after):
            kwargs['diff'] = {'before': self._before,
                              'after': self._after}
        if 'entity' not in kwargs and self._after_full:
            kwargs['entity'] = self._after_full
        super(ForemanEntityAnsibleModule, self).exit_json(**kwargs)

    @property
    def blacklisted_fields(self):
        return [key for key, value in self.foreman_spec.items() if value.get('no_log', False)]


class ForemanTaxonomicEntityAnsibleModule(ForemanEntityAnsibleModule):
    def __init__(self, argument_spec=None, **kwargs):
        spec = dict(
            organizations=dict(type='entity_list'),
            locations=dict(type='entity_list'),
        )
        foreman_spec = kwargs.pop('foreman_spec', {})
        spec.update(foreman_spec)
        super(ForemanTaxonomicEntityAnsibleModule, self).__init__(argument_spec=argument_spec, foreman_spec=spec, **kwargs)

    def handle_taxonomy_params(self, entity_dict):
        if not self.desired_absent:
            entity_dict = entity_dict.copy()

            if 'locations' in entity_dict:
                entity_dict['locations'] = self.find_resources_by_title('locations', entity_dict['locations'], thin=True)

            if 'organizations' in entity_dict:
                entity_dict['organizations'] = self.find_resources_by_name('organizations', entity_dict['organizations'], thin=True)

        return entity_dict


class KatelloAnsibleModule(KatelloMixin, ForemanAnsibleModule):
    def __init__(self, argument_spec=None, **kwargs):
        _argument_spec = dict(
            organization=dict(required=True),
        )
        if argument_spec:
            _argument_spec.update(argument_spec)
        super(KatelloAnsibleModule, self).__init__(argument_spec=_argument_spec, **kwargs)


class KatelloEntityAnsibleModule(KatelloMixin, ForemanEntityAnsibleModule):
    def __init__(self, entity_spec=None, entity_scope=None, **kwargs):
        _entity_spec = dict(
            organization=dict(type='entity', required=True),
        )
        if entity_spec:
            _entity_spec.update(entity_spec)
        if entity_scope and not entity_scope == 'organization':
            # Fail with a warning, until scope can be a list
            self.fail_json('You cannot have two entity_scopes.')
        _entity_scope = 'organization'
        super(KatelloEntityAnsibleModule, self).__init__(entity_spec=_entity_spec, entity_scope=_entity_scope, **kwargs)


def _foreman_spec_helper(spec):
    """Extend an entity spec by adding entries for all flat_names.
    Extract ansible compatible argument_spec on the way.
    """
    foreman_spec = {'id': {}}
    argument_spec = {}

    _FILTER_SPEC_KEYS = ['thin', 'scope', 'resource_type', 'search_by', 'search_operator', 'resolve', 'ensure']

    # _foreman_spec_helper() is called before we call check_requirements() in the __init__ of ForemanAnsibleModule 
    # and thus before the if HAS APYPIE check happens.
    # We have to ensure that apypie is available before using it.
    # There is two cases where we can call _foreman_spec_helper() without apypie available:
    # * When the user calls the module but doesn't have the right Python libraries installed.
    #   In this case nothing will works and the module will warn teh user to install the required library.
    # * When Ansible generates docs from the argument_spec. As the inflector is only used to build foreman_spec and not argument_spec,
    #   This is not a problem.
    #
    # So in conclusion, we only have to verify that apypie is available before using it.
    if HAS_APYPIE:
        inflector = apypie.Inflector()
    for key, value in spec.items():
        entity_value = {}
        argument_value = {k: v for (k, v) in value.items() if k not in _FILTER_SPEC_KEYS}
        flat_name = argument_value.pop('flat_name', None)

        if argument_value.get('type') == 'entity':
            entity_value['type'] = argument_value.pop('type')
            if not flat_name:
                flat_name = '{0}_id'.format(key)
        elif argument_value.get('type') == 'entity_list':
            argument_value['type'] = 'list'
            if argument_value.get('elements') is None:
                argument_value['elements'] = 'str'
            if HAS_APYPIE and not flat_name:
                flat_name = '{0}_ids'.format(inflector.singularize(key))
            entity_value['type'] = 'entity_list'
        elif argument_value.get('type') == 'nested_list':
            argument_value['type'] = 'list'
            argument_value['elements'] = 'dict'
            _dummy, argument_value['options'] = _foreman_spec_helper(argument_value.pop('foreman_spec'))
            entity_value = None
        elif 'type' in argument_value:
            entity_value['type'] = argument_value['type']

        if flat_name:
            entity_value['flat_name'] = flat_name
            foreman_spec[flat_name] = {}
            if 'type' in argument_value:
                foreman_spec[flat_name]['type'] = argument_value['type']

        if entity_value is not None:
            foreman_spec[key] = entity_value

        if argument_value.get('type') != 'invisible':
            argument_spec[key] = argument_value

    return foreman_spec, argument_spec


def _flatten_entity(entity, foreman_spec):
    """Flatten entity according to spec"""
    result = {}
    if entity is None:
        entity = {}
    for key, value in entity.items():
        if key in foreman_spec and value is not None:
            spec = foreman_spec[key]
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
    if not HAS_PYYAML:
        module.fail_json(msg='The PyYAML Python module is required', exception=PYYAML_IMP_ERR)

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
        module.fail_json(msg='Error while parsing template: ' + to_native(e))
    return template_dict


def parse_template_from_file(file_name, module):
    try:
        with open(file_name) as input_file:
            template_content = input_file.read()
            template_dict = parse_template(template_content, module)
    except Exception as e:
        module.fail_json(msg='Error while reading template file: ' + to_native(e))
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


# Helper constants
OS_LIST = ['AIX',
           'Altlinux',
           'Archlinux',
           'Coreos',
           'Debian',
           'Freebsd',
           'Gentoo',
           'Junos',
           'NXOS',
           'Rancheros',
           'Redhat',
           'Solaris',
           'Suse',
           'Windows',
           'Xenserver',
           ]

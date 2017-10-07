# -*- coding: utf-8 -*-
# (c) Bernhard Hopfenmüller (ATIX AG) 2017
# (c) Matthias Dellweg (ATIX AG) 2017
# (c) Andrew Kofink (Red Hat) 2017

import sys

from nailgun.config import ServerConfig
from nailgun.entities import (
    Entity,
    CommonParameter,
    ContentView,
    ContentViewVersion,
    LifecycleEnvironment,
    Location,
    OperatingSystem,
    Organization,
    Ping,
    Product,
    Realm,
    Repository,
    RepositorySet,
    TemplateKind,
    AbstractComputeResource,
    OSDefaultTemplate,
    ComputeProfile,
)
from nailgun import entity_mixins, entity_fields


class CommonParameter(
    CommonParameter,
    entity_mixins.Entity,
    entity_mixins.EntityCreateMixin,
    entity_mixins.EntityDeleteMixin,
    entity_mixins.EntityReadMixin,
    entity_mixins.EntitySearchMixin,
    entity_mixins.EntityUpdateMixin,
):
    pass


class VMWareComputeResource(AbstractComputeResource):  # pylint:disable=R0901
    def __init__(self, server_config=None, **kwargs):
        self._fields = {
            'set_console_password': entity_fields.BooleanField(),
            'user': entity_fields.StringField(),
            'password': entity_fields.StringField(),
            'datacenter': entity_fields.StringField()
        }
        super(VMWareComputeResource, self).__init__(server_config, **kwargs)
        self._fields['provider'].default = 'Vmware'
        self._fields['provider'].required = True
        self._fields['provider_friendly_name'].default = 'VMware'

    def read(self, entity=None, attrs=None, ignore=None, params=None):
        if attrs is None:
            attrs = self.read_json()

        if ignore is None:
            ignore = set()

        ignore.add('password')

        return super(VMWareComputeResource, self).read(entity=entity, attrs=attrs, ignore=ignore)


class OVirtComputeResource(AbstractComputeResource):  # pylint:disable=R0901
    def __init__(self, server_config=None, **kwargs):
        self._fields = {
            'set_console_password': entity_fields.BooleanField(),
            'user': entity_fields.StringField(),
            'password': entity_fields.StringField()
        }
        super(OVirtComputeResource, self).__init__(server_config, **kwargs)
        self._fields['provider'].default = 'Ovirt'
        self._fields['provider'].required = True
        self._fields['provider_friendly_name'].default = 'OVirt'

    def read(self, entity=None, attrs=None, ignore=None, params=None):
        if attrs is None:
            attrs = self.read_json()

        if ignore is None:
            ignore = set()

        ignore.add('password')

        return super(OVirtComputeResource, self).read(entity=entity, attrs=attrs, ignore=ignore)


class ComputeProfile(ComputeProfile, entity_mixins.EntitySearchMixin):
    pass


# Connection helper
def create_server(server_url, auth, verify_ssl):
    entity_mixins.DEFAULT_SERVER_CONFIG = ServerConfig(
        url=server_url,
        auth=auth,
        verify=verify_ssl,
    )


# Prerequisite: create_server
def ping_server(module):
    try:
        return Ping().search_json()
    except Exception as e:
        module.fail_json(msg="Failed to connect to Foreman server: %s " % e)


def update_fields(new, old, fields):
    needs_update = False
    for field in fields:
        if hasattr(new, field) and hasattr(old, field):
            new_attr = getattr(new, field)
            old_attr = getattr(old, field)
            id_attrs = hasattr(new_attr, 'id') and hasattr(old_attr, 'id')
            if old_attr is None or (id_attrs and new_attr.id != old_attr.id) or (not id_attrs and new_attr != old_attr):
                setattr(old, field, new_attr)
                needs_update = True
        elif hasattr(old, field) and getattr(old, field) is not None and not hasattr(new, field):
            setattr(old, field, None)
            needs_update = True
    return needs_update, old


# Common functionality to manipulate entities
def naildown_entity_state(entity_class, entity_dict, entity, state, module):
    """ Ensure that a given entity has a certain state """
    changed = False
    if state == 'present_with_defaults':
        if entity is None:
            changed = create_entity(entity_class, entity_dict, module)
    elif state == 'present':
        if entity is None:
            changed = create_entity(entity_class, entity_dict, module)
        else:
            changed = update_entity(entity, entity_dict, module)
    elif state == 'absent':
        if entity is not None:
            changed = delete_entity(entity, module)
    else:
        module.fail_json(msg='Not a valid state: {}'.format(state))
    return changed


def find_entities(entity_class, **kwargs):
    """ Find entities by certain criteria """
    return entity_class().search(
        query={'search': ','.join(['{0}="{1}"'.format(
            key, kwargs[key]) for key in kwargs]), 'per_page': sys.maxint}
    )


def find_entities_by_name(entity_class, name_list, module):
    """ Find entities of a given class by their names """
    return_list = []
    for element in name_list:
        try:
            return_list.append(find_entities(entity_class, name=element)[0])
        except Exception:
            module.fail_json(
                msg='Could not find the {0} {1}'.format(
                    entity_class.__name__, element))
    return return_list


def create_entity(entity_class, entity_dict, module):
    try:
        entity = entity_class(**entity_dict)
        if not module.check_mode:
            entity.create()
    except Exception as e:
        module.fail_json(msg='Error while creating {0}: {1}'.format(
            entity_class.__name__, str(e)))
    return True


def fields_equal(value1, value2):
    # field contains an Entity
    if isinstance(value1, Entity) and isinstance(value2, Entity):
        return value1.id == value2.id
    # field contains a list of possibly Entities
    if isinstance(value1, list) and isinstance(value2, list):
        entity_ids_1 = set(entity.id for entity in value1 if isinstance(entity, Entity))
        entity_ids_2 = set(entity.id for entity in value2 if isinstance(entity, Entity))
        fields1 = set(field for field in value1 if not isinstance(field, Entity))
        fields2 = set(field for field in value2 if not isinstance(field, Entity))
        return entity_ids_1 == entity_ids_2 and fields1 == fields2
    # 'normal' value
    return value1 == value2


def update_entity(old_entity, entity_dict, module):
    try:
        volatile_entity = old_entity.read()
        fields = []
        for key, value in volatile_entity.get_values().iteritems():
            if key in entity_dict and not fields_equal(value, entity_dict[key]):
                volatile_entity.__setattr__(key, entity_dict[key])
                fields.append(key)
        if len(fields) > 0:
            if not module.check_mode:
                volatile_entity.update(fields)
            return True
        return False
    except Exception as e:
        module.fail_json(msg='Error while updating {0}: {1}'.format(
            old_entity.__class__.__name__, str(e)))


def delete_entity(entity, module):
    try:
        if not module.check_mode:
            entity.delete()
    except Exception as e:
        module.fail_json(msg='Error while deleting {0}: {1}'.format(
            entity.__class__.__name__, str(e)))
    return True


def find_content_view(module, name, organization, failsafe=False):
    content_view = ContentView(name=name, organization=organization)
    return handle_find_response(module, content_view.search(), message="No content view found for %s" % name, failsafe=failsafe)


def find_content_view_version(module, content_view, environment=None, version=None, failsafe=False):
    if environment is not None:
        response = ContentViewVersion(content_view=content_view).search(['content_view'], {'environment_id': environment.id})
        return handle_find_response(module, response, message="No content view version found on content view {} promoted to environment {}".
                                    format(content_view.name, environment.name), failsafe=failsafe)
    elif version is not None:
        response = ContentViewVersion(content_view=content_view, version=version).search()
        return handle_find_response(module, response, message="No content view version found on content view {} for version {}".
                                    format(content_view.name, version), failsafe=failsafe)


def find_organization(module, name, failsafe=False):
    org = Organization(name=name).search(set(), {'search': 'name="{}"'.format(name)})
    return handle_find_response(module, org, message="No organization found for %s" % name, failsafe=failsafe)

def find_location(module, name, failsafe=False):
    loc = Location(name=name).search(set(), {'search': 'name="{}"'.format(name)})
    return handle_find_response(module, loc, message="No location found for %s" % name, failsafe=failsafe)


def find_compute_resource(module, name, failsafe=False):
    compute_resource = AbstractComputeResource(name=name).search(set(), {'search': 'name="{}"'.format(name)})
    return handle_find_response(module, compute_resource, message="No compute resource found for %s" % name, failsafe=failsafe)


def find_compute_profile(module, name, failsafe=False):
    compute_profile = ComputeProfile(name=name).search(set(), {'search': 'name="{}"'.format(name)})
    return handle_find_response(module, compute_profile, message="No compute profile found for %s" % name, failsafe=failsafe)


def find_lifecycle_environment(module, name, organization, failsafe=False):
    response = LifecycleEnvironment(name=name, organization=organization).search()
    return handle_find_response(module, response, message="No lifecycle environment found for %s" % name, failsafe=failsafe)


def find_product(module, name, organization, failsafe=False):
    product = Product(name=name, organization=organization)
    del(product._fields['sync_plan'])
    return handle_find_response(module, product.search(), message="No product found for %s" % name, failsafe=failsafe)


def find_repositories(module, repositories, product):
    return map(lambda repository: find_repository(module, repository, product), repositories)


def find_repository(module, name, product):
    repository = Repository(name=name, product=product)
    return handle_find_response(module, repository.search(), message="No Repository found for %s" % name)


def find_repository_set(module, name, product, failsafe=False):
    repo_set = RepositorySet(name=name, product=product)
    return handle_find_response(module, repo_set.search(), message="No repository set found for %s" % name, failsafe=failsafe)


def find_operating_system_by_title(module, title, failsafe=False):
    response = OperatingSystem().search(set(), {'search': 'title~"{}"'.format(title)})
    return handle_find_response(module, response, message="No unique Operating System found with title %s" % title, failsafe=failsafe)


def find_os_default_template(module, operatingsystem, template_kind, failsafe=False):
    response = OSDefaultTemplate(operatingsystem=operatingsystem).search()
    response = [item for item in response if item.template_kind.id == template_kind.id]
    return handle_find_response(module, response, message="No default template found for %s/%s" % (operatingsystem.name, template_kind.name), failsafe=failsafe)


def handle_find_response(module, response, message=None, failsafe=False):
    message = "Find failed for entity: %s" % response if message is None else message
    if len(response) == 1:
        return response[0]
    elif failsafe:
        return None
    else:
        module.fail_json(msg=message)


def current_subscription_manifest(module, organization):
    org_json = organization.read_json()
    if 'owner_details' in org_json and 'upstreamConsumer' in org_json['owner_details']:
        return org_json['owner_details']['upstreamConsumer']


def set_task_timeout(timeout_ms):
    entity_mixins.TASK_TIMEOUT = timeout_ms

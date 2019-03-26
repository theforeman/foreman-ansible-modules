# -*- coding: utf-8 -*-
# (c) Bernhard Hopfenmüller (ATIX AG) 2017
# (c) Matthias Dellweg (ATIX AG) 2017
# (c) Andrew Kofink (Red Hat) 2017

import sys

from nailgun.config import ServerConfig
from nailgun.entities import (
    AbstractComputeResource,
    AbstractContentViewFilter,
    ActivationKey,
    Bookmark,
    CommonParameter,
    ComputeAttribute,
    ComputeProfile,
    ContentCredential,
    ContentView,
    ContentViewFilterRule,
    ContentViewVersion,
    Domain,
    Entity,
    Environment,
    Errata,
    File,
    JobTemplate,
    Host,
    HostGroup,
    LifecycleEnvironment,
    Location,
    Media,
    OperatingSystem,
    Organization,
    OSDefaultTemplate,
    OVirtComputeResource,
    Package,
    PackageGroup,
    Ping,
    Product,
    Realm,
    Repository,
    RepositorySet,
    Setting,
    SmartProxy,
    Subnet,
    Subnet,
    Subscription,
    SyncPlan,
    TemplateInput,
    TemplateKind,
    VMWareComputeResource,
)
from nailgun import entity_mixins

from ansible.module_utils.parsing.convert_bool import boolean


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


def sanitize_entity_dict(entity_dict, name_map):
    return {value: entity_dict[key] for key, value in name_map.items() if key in entity_dict}


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
def naildown_entity_state(entity_class, entity_dict, entity, state, module, check_missing=None, check_type=None, force_update=None):
    changed, _ = naildown_entity(entity_class, entity_dict, entity, state, module, check_missing, check_type, force_update)
    return changed


def naildown_entity(entity_class, entity_dict, entity, state, module, check_missing=None, check_type=None, force_update=None):
    """ Ensure that a given entity has a certain state """
    changed, changed_entity = False, entity
    if state == 'present_with_defaults':
        if entity is None:
            changed, changed_entity = create_entity(entity_class, entity_dict, module)
    elif state == 'present':
        if entity is None:
            changed, changed_entity = create_entity(entity_class, entity_dict, module)
        else:
            changed, changed_entity = update_entity(entity, entity_dict, module, check_missing, check_type, force_update)
    elif state == 'copied':
        new_entity = entity_class(name=entity_dict['new_name'], organization=entity_dict['organization']).search()
        if entity is not None and len(new_entity) == 0:
            changed, changed_entity = copy_entity(entity, entity_dict, module)
        elif len(new_entity) == 1:
            changed_entity = new_entity[0]
    elif state == 'absent':
        if entity is not None:
            changed, changed_entity = delete_entity(entity, module)
    else:
        module.fail_json(msg='Not a valid state: {}'.format(state))
    return changed, changed_entity


def query_power_state(module, host):
    return host.power(data={'power_action': 'state'})['power']


def naildown_power_state(module, host, state):
    changed = False
    curr_state = query_power_state(module, host)
    if curr_state != state:
        host.power(data={'power_action': state})['power']
        changed = True
    return changed


def search_entities_json(entity_class, search):
    """ Find entities using search """
    return entity_class().search_json(
        query={'search': '{0}'.format(search),
               # This is a hack to work around pagination in API-V2
               # See Redmine: #21800
               'per_page': 2 << 31}
    )


def find_entities(entity_class, **kwargs):
    """ Find entities by certain criteria """
    return entity_class().search(
        query={'search': ','.join(['{0}="{1}"'.format(
            key, kwargs[key]) for key in kwargs]),
            # This is a hack to work around pagination in API-V2
            # See Redmine: #21800
            'per_page': 2 << 31}
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
        result = None
        entity = entity_class(**entity_dict)
        if not module.check_mode:
            result = entity.create()
    except Exception as e:
        module.fail_json(msg='Error while creating {0}: {1}'.format(
            entity_class.__name__, str(e)))
    return True, result


def copy_entity(entity, entity_dict, module):
    try:
        result = None
        if not module.check_mode:
            result = entity.copy(data={'new_name': entity_dict['new_name']})
    except Exception as e:
        module.fail_json(msg='Error while copying {0}: {1}'.format(
            entity.__class__.__name__, str(e)))
    return True, result


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


def update_entity(old_entity, entity_dict, module, check_missing, check_type, force_update):
    try:
        volatile_entity = old_entity.read()
        result = volatile_entity
        fields = []
        for key, value in volatile_entity.get_values().items():
            if key in entity_dict:
                if check_type and not isinstance(value, type(entity_dict[key])):
                    if isinstance(value, bool):
                        entity_dict[key] = boolean(entity_dict[key])
                    elif isinstance(value, list):
                        entity_dict[key] = str(sorted(entity_dict[key].split(',')))
                        value = str(sorted([str(v) for v in value]))
                    else:
                        if value is None:
                            value = ""
                        entity_dict[key] = type(value)(entity_dict[key])
                if not fields_equal(value, entity_dict[key]):
                    volatile_entity.__setattr__(key, entity_dict[key])
                    fields.append(key)
            # check_missing is a special case, Foreman sometimes returns different values
            # depending on what 'type' of same object you are requesting. Content View
            # Filters are a prime example. We list these attributes in `check_missing`
            # so we can ensure the entity is as the user specified.
            if check_missing is not None and key not in entity_dict and key in check_missing:
                volatile_entity.__setattr__(key, None)
                fields.append(key)
        if force_update:
            for key in force_update:
                fields.append(key)
        if check_missing is not None:
            for key in check_missing:
                if key in entity_dict and key not in volatile_entity.get_values():
                    volatile_entity.__setattr__(key, entity_dict[key])
                    fields.append(key)
        if len(fields) > 0:
            if not module.check_mode:
                result = volatile_entity.update(fields)
            return True, result
        return False, result
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
    return True, None


def find_activation_key(module, name, organization, failsafe=False):
    activation_key = ActivationKey(name=name, organization=organization)
    return handle_find_response(module, activation_key.search(), message="No activation key found for %s" % name, failsafe=failsafe)


def find_bookmark(module, name, controller, failsafe=False):
    bookmark = Bookmark().search(query={'search': 'name="{}",controller="{}"'.format(name, controller)})
    return handle_find_response(module, bookmark, message="No bookmark found for %s" % name, failsafe=failsafe)


def find_package_group(module, name, failsafe=False):
    package_group = PackageGroup().search(set(), {'search': 'name="{}"'.format(name)})
    return handle_find_response(module, package_group, message="No package group found for %s" % name, failsafe=failsafe)


def find_errata(module, id, organization, failsafe=False):
    errata = Errata().search(set(), {'search': 'id="{}"'.format(id)})
    return handle_find_response(module, errata, message="No errata found for %s" % id, failsafe=failsafe)


def find_content_view(module, name, organization, failsafe=False):
    content_view = ContentView(name=name, organization=organization)
    return handle_find_response(module, content_view.search(), message="No content view found for %s" % name, failsafe=failsafe)


def find_content_views(module, content_views, organization, failsafe=False):
    return list(map(lambda content_view: find_content_view(module, content_view, organization, failsafe), content_views))


def find_content_view_version(module, content_view, environment=None, version=None, failsafe=False):
    if environment is not None:
        response = ContentViewVersion(content_view=content_view).search(['content_view'], {'environment_id': environment.id})
        return handle_find_response(module, response, message="No content view version found on content view {} promoted to environment {}".
                                    format(content_view.name, environment.name), failsafe=failsafe)
    elif version is not None:
        response = ContentViewVersion(content_view=content_view, version=version).search()
        return handle_find_response(module, response, message="No content view version found on content view {} for version {}".
                                    format(content_view.name, version), failsafe=failsafe)


def find_content_view_versions(module, content_views, environment=None, version=None, failsafe=False):
    return list(map(lambda content_view: find_content_view_version(module, content_view, environment, version, failsafe), content_views))


def find_content_view_filter_rule(module, content_view_filter, name=False, errata=False, failsafe=False):
    if errata is not False:
        content_view_filter_rule = ContentViewFilterRule(content_view_filter=content_view_filter, errata=errata).search()
    else:
        content_view_filter_rule = ContentViewFilterRule(name=name, content_view_filter=content_view_filter).search()
    return handle_find_response(module, content_view_filter_rule, message="No content view filter rule found for %s" % name or errata, failsafe=failsafe)


def find_content_view_filter(module, name, content_view, failsafe=False):
    content_view_filter = AbstractContentViewFilter(name=name, content_view=content_view)
    return handle_find_response(module, content_view_filter.search(), message="No content view filter found for %s" % name, failsafe=failsafe)


def find_host(module, name, failsafe=False):
    host = Host().search(set(), {'search': 'name="{}"'.format(name)})
    return handle_find_response(module, host, message="No host found for %s" % name, failsafe=failsafe)


def find_hostgroup(module, name, failsafe=False):
    hostgroup = HostGroup().search(set(), {'search': 'name="{}"'.format(name)})
    return handle_find_response(module, hostgroup, message="No hostgroup found for %s" % name, failsafe=failsafe)


def find_organizations(module, organizations):
    return list(map(lambda organization: find_organization(module, organization), organizations))


def find_organization(module, name, failsafe=False):
    org = Organization(name=name).search(set(), {'search': 'name="{}"'.format(name)})
    return handle_find_response(module, org, message="No organization found for %s" % name, failsafe=failsafe)


def find_locations(module, locations):
    return list(map(lambda location: find_location(module, location), locations))


def find_location(module, title, failsafe=False):
    loc = Location(name=title.split('/')[-1]).search(set(), {'search': 'title="{}"'.format(title)})
    return handle_find_response(module, loc, message="No location found for %s" % title, failsafe=failsafe)


def find_compute_resource(module, name, failsafe=False):
    compute_resource = AbstractComputeResource(name=name).search(set(), {'search': 'name="{}"'.format(name)})
    return handle_find_response(module, compute_resource, message="No compute resource found for %s" % name, failsafe=failsafe)


def find_compute_profile(module, name, failsafe=False):
    compute_profile = ComputeProfile(name=name).search(set(), {'search': 'name="{}"'.format(name)})
    return handle_find_response(module, compute_profile, message="No compute profile found for %s" % name, failsafe=failsafe)


def find_compute_attribute(module, compute_profile_name, compute_resource_name, failsafe=False):
    search = {'search': 'compute_profile="{}" and compute_resource="{}"'.format(compute_profile_name, compute_resource_name)}
    compute_attribute = ComputeAttribute().search(set(), search)
    return handle_find_response(module, compute_attribute, message="No compute attribute found for %s %s" % (compute_profile_name, compute_resource_name),
                                failsafe=failsafe)


def find_domains(module, names, failsafe=False):
    return list(map(lambda name: find_domain(module, name, failsafe=failsafe), names))


def find_domain(module, name, failsafe=False):
    domain = Domain().search(query={'search': 'name="{}"'.format(name)})
    return handle_find_response(module, domain, message="No domain found for %s" % name, failsafe=failsafe)


def find_environment(module, name, failsafe=False):
    env = Environment().search(query={'search': 'name="{}"'.format(name)})
    return handle_find_response(module, env, message="No environment found for %s" % name, failsafe=failsafe)


def find_subnet(module, name, failsafe=False):
    subnet = Subnet().search(query={'search': 'name="{}"'.format(name)})
    return handle_find_response(module, subnet, message="No subnet found for %s" % name, failsafe=failsafe)


def find_installation_medium(module, name, failsafe=False):
    medium = Media().search(query={'search': 'name="{}"'.format(name)})
    return handle_find_response(module, medium, message="No installation medium found for %s" % name, failsafe=failsafe)


def find_lifecycle_environments(module, names, organization, failsafe=False):
    return list(map(lambda name: find_lifecycle_environment(module, name, organization, failsafe=failsafe), names))


def find_lifecycle_environment(module, name, organization, failsafe=False):
    response = LifecycleEnvironment(name=name, organization=organization).search()
    return handle_find_response(module, response, message="No lifecycle environment found for %s" % name, failsafe=failsafe)


def find_product(module, name, organization, failsafe=False):
    product = Product(name=name, organization=organization)
    return handle_find_response(module, product.search(), message="No product found for %s" % name, failsafe=failsafe)


def find_products(module, names, organization, failsafe=False):
    return list(map(lambda name: find_product(module, name, organization, failsafe=failsafe), names))


def find_sync_plan(module, name, organization, failsafe=False):
    response = SyncPlan(name=name, organization=organization).search()
    return handle_find_response(module, response, message="No sync plan found for %s" % name, failsafe=failsafe)


def find_repositories(module, repositories, organization, failsafe=False):
    products = dict()
    for repository in repositories:
        if repository['product'] not in products:
            products[repository['product']] = find_product(module, repository['product'], organization)
    return list(map(lambda repository: find_repository(module, repository['name'], products[repository['product']], failsafe=failsafe), repositories))


def find_repository(module, name, product, failsafe=False):
    repository = Repository(name=name, product=product)
    return handle_find_response(module, repository.search(), message="No Repository found for %s" % name, failsafe=failsafe)


def find_content_credential(module, name, organization, failsafe=False):
    content_credential = ContentCredential(name=name, organization=organization)
    return handle_find_response(module, content_credential.search(), message="No content credential found for %s" % name, failsafe=failsafe)


def find_repository_set(module, name=None, product=None, organization=None, label=None, failsafe=False):
    if label and organization:
        repo_set = RepositorySet(organization=organization).search(query={'search': 'label="{}"'.format(label)})
    elif name and organization:
        repo_set = RepositorySet(name=name, organization=organization).search()
    else:
        repo_set = RepositorySet(name=name, product=product).search()
    return handle_find_response(module, repo_set, message="No repository set found for %s" % name or label, failsafe=failsafe)


def find_setting(module, name, failsafe=False):
    setting = Setting(name=name).search(set(), {'search': 'name="{}"'.format(name)})
    return handle_find_response(module, setting, message="No setting found for %s" % name, failsafe=failsafe)


def find_smart_proxies(module, names, failsafe=False):
    return list(map(lambda name: find_smart_proxy(module, name, failsafe=failsafe), names))


def find_smart_proxy(module, name, failsafe=False):
    smart_proxy = SmartProxy().search(query={'search': 'name="{}"'.format(name)})
    return handle_find_response(module, smart_proxy, message="No Smart Proxy found for %s" % name, failsafe=failsafe)


def find_subscription(module, name, organization, failsafe=False):
    subscription = Subscription(organization=organization)
    return handle_find_response(module, subscription.search(query={'search': 'name="{}"'.format(name)}),
                                message="No subscription found for %s" % name, failsafe=failsafe)


def find_subscriptions(module, subscriptions, organization, failsafe=False):
    return map(lambda subscription: find_subscription(module, subscription['name'], organization, failsafe), subscriptions)


def find_template_input(module, name, template, failsafe=True):
    responses = TemplateInput(template=template).search()
    response = [ti for ti in responses if ti.name == name]
    return handle_find_response(module, response, message="No template input found for <%s> in job template" % name, failsafe=failsafe)


def find_operating_systems_by_title(module, titles):
    return list(map(lambda operating_system: find_operating_system_by_title(module, operating_system), titles))


def find_operating_system_by_title(module, title, failsafe=False):
    response = OperatingSystem().search(set(), {'search': 'title~"{}"'.format(title)})
    return handle_find_response(module, response, message="No unique Operating System found with title %s" % title, failsafe=failsafe)


def find_os_default_template(module, operatingsystem, template_kind, failsafe=False):
    response = OSDefaultTemplate(operatingsystem=operatingsystem).search()
    response = [item for item in response if item.template_kind.id == template_kind.id]
    return handle_find_response(module, response, message="No default template found for %s/%s" % (operatingsystem.name, template_kind.name), failsafe=failsafe)


def find_package(module, query, repository, failsafe=False):
    package = Package(repository=repository).search(query={'search': '{}'.format(query)})
    return handle_find_response(module, package, message="No Package found for %s" % query, failsafe=failsafe)


def find_file(module, query, repository, failsafe=False):
    file = File(repository=repository).search(query={'search': '{}'.format(query)})
    return handle_find_response(module, file, message="No File found for %s" % query, failsafe=failsafe)


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

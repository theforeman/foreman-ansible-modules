# -*- coding: utf-8 -*-
# (c) Bernhard Hopfenmüller 2017
# (c) Matthias Dellweg 2017

import re
import yaml

from nailgun.config import ServerConfig
from nailgun.entities import (
    LifecycleEnvironment,
    Location,
    Organization,
    Ping,
    TemplateKind,
)


# Mix compare functionality into some entities as needed
class EntityCompareMixin:

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id


class TemplateKind(EntityCompareMixin, TemplateKind):
    pass


class Organization(EntityCompareMixin, Organization):
    pass


class Location(EntityCompareMixin, Location):
    pass


# Connection helper
def create_server(server_url, auth, verify_ssl):
    ServerConfig(
        url=server_url,
        auth=auth,
        verify=verify_ssl,
    ).save()


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
    changed = False
    if state == 'present':
        if len(entity) == 0:
            changed = create_entity(entity_class, entity_dict, module)
    elif state == 'latest':
        if len(entity) == 0:
            changed = create_entity(entity_class, entity_dict, module)
        else:
            changed = update_entity(entity[0], entity_dict, module)
    else:
        # state == 'absent'
        if len(entity) != 0:
            changed = delete_entity(entity[0], module)
    return changed


def find_entity(entity_class, **kwargs):
    return entity_class().search(
        query={'search': ','.join(['{0}="{1}"'.format(
            key, kwargs[key]) for key in kwargs])}
    )


def find_entities(entity_class, name_list, module):
    return_list = []
    for element in name_list:
        try:
            return_list.append(find_entity(entity_class, name=element)[0])
        except Exception:
            module.fail_json(
                msg='Could not find the {0} {1}'.format(
                    entity_class.__name__, element))
    return return_list


def create_entity(entity_class, entity_dict, module):
    try:
        entity = entity_class(**entity_dict)
        entity.create()
    except Exception as e:
        module.fail_json(msg='Error while creating {0}: {1}'.format(
            entity_class.__name__, str(e)))
    return True


def update_entity(old_entity, entity_dict, module):
    try:
        volatile_entity = old_entity.read()
        fields = []
        for key, value in volatile_entity.get_values().iteritems():
            if key in entity_dict and value != entity_dict[key]:
                volatile_entity.__setattr__(key, entity_dict[key])
                fields.append(key)
        if len(fields) > 0:
            volatile_entity.update(fields)
            return True
        return False
    except Exception as e:
        module.fail_json(msg='Error while updating {0}: {1}'.format(
            old_entity.__class__.__name__, str(e)))


def delete_entity(entity, module):
    try:
        entity.delete()
    except Exception as e:
        module.fail_json(msg='Error while deleting {0}: {1}'.format(
            entity.__class__.__name__, str(e)))
    return True


# Helper for templates
def parse_template(template_content, module):
    try:
        data = re.match(
            '.*\s*<%#([^%]*([^%]*%*[^>%])*%*)%>', template_content)
        if data:
            datalist = data.group(1)
            if datalist[-1] == '-':
                datalist = datalist[:-1]
            template_dict = yaml.load(datalist)
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


def find_organization(module, name, failsafe=False):
    org = Organization(name=name)
    response = org.search(set(), {'search': 'name="{}"'.format(name)})
    return handle_find_response(module, response, message="No organization found for %s" % name, failsafe=failsafe)


def find_lifecycle_environment(module, name, organization, failsafe=False):
    response = LifecycleEnvironment(name=name, organization=organization).search()
    return handle_find_response(module, response, message="No lifecycle environment found for %s" % name, failsafe=failsafe)


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

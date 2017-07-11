# -*- coding: utf-8 -*-
# (c) Bernhard Hopfenmüller 2017
# (c) Matthias Dellweg 2017

import re
import yaml

from nailgun.config import ServerConfig
import nailgun.entities


# Mix compare functionality into some entities as needed
class EntityCompareMixin:

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id


class TemplateKind(EntityCompareMixin, nailgun.entities.TemplateKind):
    pass


class Organization(EntityCompareMixin, nailgun.entities.Organization):
    pass


class Location(EntityCompareMixin, nailgun.entities.Location):
    pass


# Connection helper
def create_server(server_url, auth, verify_ssl):
    ServerConfig(
        url=server_url,
        auth=auth,
        verify=verify_ssl,
    ).save()


# Common functionality to manipulate entities
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
        except Exception as e:
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
        with open(file_name) as file:
            template_content = ''.join(file)
            template_dict = parse_template(template_content, module)
    except Exception as e:
        module.fail_json(msg='Error while reading template file: ' + str(e))
    return template_dict

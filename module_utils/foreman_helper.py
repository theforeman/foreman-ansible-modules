# -*- coding: utf-8 -*-
# (c) Matthias Dellweg (ATIX AG) 2017

import re
import yaml


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

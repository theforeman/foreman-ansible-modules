# Foreman Ansible Modules [![Build Status](https://travis-ci.org/theforeman/foreman-ansible-modules.svg?branch=master)](https://travis-ci.org/theforeman/foreman-ansible-modules)

Ansible modules for interacting with the Foreman API and various plugin APIs such as Katello.

## Goals

The intent of this repository is to be a place that community members can develop or contribute modules. The goals of this repository are:

  * centralized location for community modules
  * a single repository to clone for interacting with Foreman & plugins
  * source for the official Ansible collection

## Documentation

A list of all modules and their documentation can be found at [theforeman.org/plugins/foreman-ansible-modules](https://theforeman.org/plugins/foreman-ansible-modules/).

## Supported Foreman and plugins versions

Modules should support any currently stable Foreman release and the matching set of plugins.
Some modules have additional features/arguments that are only applied when the corresponding plugin is installed.

We actively test the modules against the latest stable Foreman release and the matching set of plugins.

## Installation

There are currently three ways to use the modules in your setup: install from Ansible Galaxy, install via RPM and run directly from Git.

### Installation from Ansible Galaxy

You can install the collection from [Ansible Galaxy](https://galaxy.ansible.com/theforeman/foreman) by running `mazer install theforeman.foreman` or `ansible-galaxy collection install theforeman.foreman`.

After the installation, the modules are available as `theforeman.foreman.<module_name>`. Please see the [Using Ansible collections documentation](https://docs.ansible.com/ansible/devel/user_guide/collections_using.html) for further details.

### Installation via RPM

The collection is also available as `ansible-collection-theforeman-foreman` from the `client` repository on `yum.theforeman.org` starting with Foreman 1.24.

After installing the RPM, you can use the modules in the same way as when they are installed directly from Ansible Galaxy.

### Run from Git

If you don't want to install the collection, or use an Ansible version that does not support collections (< 2.8), you can consume the modules directly from Git.

Just clone the [foreman-ansible-modules git repository](https://github.com/theforeman/foreman-ansible-modules.git) to your machine and add the path to the modules to `ansible.cfg`.

Let's assume you have a directory of playbooks and roles in a git repository for your infrastructure named `infra`:

```
infra/
├── ansible.cfg
├── playbooks
└── roles
```

First, clone the repository into `infra/`:

```
cd infra/
git clone https://github.com/theforeman/foreman-ansible-modules.git
```

Now edit `ansible.cfg` like this:

```
[defaults]
library = foreman-ansible-modules/plugins/modules
module_utils = foreman-ansible-modules/plugins/module_utils
doc_fragment_plugins = foreman-ansible-modules/plugins/doc_fragments
filter_plugins = foreman-ansible-modules/plugins/filter
```

As the modules are not installed inside a collection, you will have to refer to them as `<module_name>` and not as `theforeman.foreman.<module_name>`.

## Dependencies

* `PyYAML`
* [`apypie`](https://pypi.org/project/apypie/)
* [`ipaddress`](https://pypi.org/project/ipaddress/) for the `foreman_subnet` module on Python 2.7

## Supported Ansible Versions

The modules should work with Ansible >= 2.3.

As we're using Ansible's [documentation fragment](https://docs.ansible.com/ansible/devel/dev_guide/developing_modules_documenting.html#documentation-fragments) feature, that was introduced in Ansible 2.8, `ansible-doc` prior to 2.8 won't be able to display the module documentation, but the modules will still run fine with `ansible` and `ansible-playbook`.

## Supported Python Versions

Starting with Ansible 2.7, Ansible only supports Python 2.7 and 3.5 (and higher). These are also the only Python versions we develop and test the modules against.

## Branches

* `master` - current development branch, using the `apypie` library
* `nailgun` - the state of the repository before the switch to the `apypie` library started, `nailgun` is the only dependency

## How to write modules in this repository

First of all, please have a look at the [Ansible module development](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html) guide and get familiar with the general Ansible module layout.

When looking at actual modules in this repository ([`foreman_domain`](plugins/modules/foreman_domain.py) is a nice short example), you will notice a few differences to a "regular" Ansible module:

* Instead of `AnsibleModule`, we use `ForemanEntityAnsibleModule` (and a few others, see [`plugins/module_utils/foreman_helper.py`](plugins/module_utils/foreman_helper.py)) which provides an abstraction layer for talking with the Foreman API
* Instead of Ansible's `argument_spec`, we provide an enhanced version called `entity_spec`. It handles the translation from Ansible module arguments to Foreman API parameters, as nobody wants to write `organization_ids` in their playbook when they can write `organizations`

The rest of the module is usually very minimalistic:

* Connect to the API (`module.connect()`)
* Find the entity if it already exists (`entity = module.find_resource_by_name(…)`)
* Adjust the data of the entity if desired
* Ensure the entity state and details (`changed = module.ensure_resource_state(…)`)

### Specification of the `entity_spec`

The `entity_spec` can be seen as an extended version of Ansible's `argument_spec`. It understands more parameters (e.g. `flat_name`) and supports more `type`s than the original version. An `argument_spec` will be generated from an `entity_spec`. Any parameters not directly known or consumed by `entity_spec` will be passed directly to the `argument_spec`.

In addition to Ansible's `argument_spec`, `entity_spec` understands the following types:

* `type='entity'` The referenced value is another Foreman entity.
This is usually combined with `flat_name=<entity>_id`.
* `type='entity_list'` The referenced value is a list of Foreman entities.
This is usually combined with `flat_name=<entity>_ids`.
* `type='nested_list'` The referenced value is a list of Foreman entities that are not included in the main API call.
The module must handle the entities separately.
See domain parameters in [`foreman_domain`](plugins/modules/foreman_domain.py) for an example.
The sub entities must be described by `entity_spec=<sub_entity>_spec`.
* `type='invisible'` The parameter is available to the API call, but it will be excluded from Ansible's `argument_spec`.

`flat_name` provides a way to translate the name of a module argument as known to Ansible to the name understood by the Foreman API.

You can add new or override generated Ansible module arguments, by specifying them in the `argument_spec` as usual.



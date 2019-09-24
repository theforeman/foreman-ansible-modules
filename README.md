# Foreman Ansible Modules [![Build Status](https://travis-ci.org/theforeman/foreman-ansible-modules.svg?branch=master)](https://travis-ci.org/theforeman/foreman-ansible-modules)

Ansible modules for interacting with the Foreman API and various plugin APIs such as Katello.

## Goals

The intent of this repository is to be a place that community members can develop or contribute modules. The goals of this repository are:

  * centralized location for community modules
  * a single repository to clone for interacting with Foreman & plugins
  * source for the official Ansible collection

## Documentation

A list of all modules and their documentation can be found at [theforeman.org/plugins/foreman-ansible-modules](https://theforeman.org/plugins/foreman-ansible-modules/).

Documentation how to [write](docs/developing.md), [test](docs/testing.md) and [debug](docs/debugging.md) modules is available in the [`docs`](docs/) folder.

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

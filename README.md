# Foreman Ansible Modules [![Build Status](https://travis-ci.org/theforeman/foreman-ansible-modules.svg?branch=master)](https://travis-ci.org/theforeman/foreman-ansible-modules)

This repository contains Ansible modules for interacting with the Foreman API and various plugin APIs such as Katello.

## Goals

The intent of this repository is to be a place that community members can develop or contribute modules. The goals of this repository are:

  * centralized location for community modules
  * a single repository to clone for interacting with Foreman & plugins
  * source for the official Ansible collection (TBD)

## Branches

* `master` - current development branch, using both `nailgun` and `apypie` libraries. The progress of the `nailgun` to `apypie` migration can be seen in [issue #274](https://github.com/theforeman/foreman-ansible-modules/issues/274)
* `nailgun` - the state of the repository before the switch to the `apypie` library started, `nailgun` is the only dependency

## Supported Foreman and plugins versions

### `apypie` based modules

Modules that use the `apypie` library should support any currently stable Foreman release and the matching set of plugins.
Some modules have additional features/arguments that are only applied when the corresponding plugin is installed.

We actively test the modules against the latest stable Foreman release and the matching set of plugins.

### `nailgun` based modules

The `nailgun` library has specific releases for different Satellite (and thus Foreman/Katello) releases.
Please pick the right `nailgun` release from the table below for your environment.

We actively test the modules against the latest stable Foreman release and the matching set of plugins.

#### `nailgun` versions

Below is listed the correct Nailgun version/branch for your environment

Server                       | Nailgun branch | Nailgun version
---------------------------- | ------ | ------
Katello 3.11 and newer       | master | 0.32.x
Satellite 6.5 / Katello 3.10 | 6.5.z  | 0.32.x
Satellite 6.4 / Katello 3.7  | 6.4.z  | 0.30.x
Satellite 6.3 / Katello 3.4  | 6.3.z  | 0.30.x

## How To Use The Repository

The following is an example of how you could use this repository in your own environment. Let's assume you have a directory of playbooks and roles in a git repository for your infrastructure named `infra`:

```
infra/
├── playbooks
└── roles
```

First, clone this repository into `infra/`:

```
cd infra/
git clone https://github.com/theforeman/foreman-ansible-modules.git
```

Note the `ansible.cfg` file cloned with foreman-ansible-modules. The ansible.cfg
needs to be in your current directory when you run `ansible` or
`ansible-playbook`. You can copy it to another location or add it to your
current ansible configuration; make sure to update the relative paths to the
foreman-ansible-module `modules` and `module_utils` if you do so.

Now your playbooks and roles should have access to the `modules` and `module_utils`
contained in the repository for use, testing, or development of new modules.

## How to write modules in this repository

First of all, please have a look at the [Ansible module development](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html) guide and get familiar with the general Ansible module layout.

When looking at actual modules in this repository ([`foreman_domain`](plugins/modules/foreman_domain.py) is a nice short example), you will notice a few differences to a "regular" Ansible module:

* Instead of `AnsibleModule`, we use `ForemanEntityApypieAnsibleModule` (and a few others, see [`plugins/module_utils/foreman_helper.py`](plugins/module_utils/foreman_helper.py)) which provides an abstraction layer for talking with the Foreman API
* Instead of Ansible's `argument_spec`, we provide an enhanced version called `entity_spec`. It handles the translation from Ansible module arguments to Foreman API parameters, as nobody wants to write `organization_ids` in their playbook when they can write `organizations`

The rest of the module is usually very minimalistic:

* Connect to the API (`module.connect()`)
* Find the entity if it already exists (`entity = module.find_resource_by_name(…)`)
* Adjust the data of the entity if desired
* Ensure the entity state and details (`changed = module.ensure_resource_state(…)`)

Please note: we currently have modules that use `apypie` and `nailgun` as the backend libraries to talk to the API, but we would prefer not to add any new modules using `nailgun` and focus on migrating everything to `apypie`.

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

## How to test modules in this repository

To test, you need a running instance of Foreman, probably with Katello (use [forklift](https://github.com/theforeman/forklift) if unsure).
Also you need to run `make test-setup` and update `tests/test_playbooks/vars/server.yml`:

```sh
make test-setup
vi tests/test_playbooks/vars/server.yml # point to your Foreman instance
```

To run the tests using the `foreman_global_parameter` module as an example:

```sh
make test # all tests
make test_global_parameter  # single test
make test TEST="-k 'organzation or global_parameter'"  # select tests by expression (see `pytest -h`)
```

The tests are run against prerecorded server-responses.
You can (re-)record the cassettes for a specific test with

```sh
make record_global_parameter
```

See also [Guidedeline to writing tests](tests/README.md).

## How to debug modules in this repository

Set up debugging using ansible's test-module

```sh
make debug-setup
```

Debug with ansible's test-module

```sh
make debug MODULE=<module name>

# Example: debug the katello_content_view module
$ make debug MODULE=katello_content_view
./.tmp/ansible/hacking/test-module -m modules/katello_content_view.py -a @tests/data/content-view.json -D /usr/lib64/python2.7/pdb.py
...
```

You can set a number of environment variables besides `MODULE` to configure make. Check the [Makefile](https://github.com/theforeman/foreman-ansible-modules/blob/master/Makefile) for more configuration options.

## Modules List

This is a list of modules currently in the repository (please add to the list if adding a module).

#### Entity Modules

 * foreman_architecture: create and maintain architectures
 * foreman_compute_attribute: create and maintain compute attributes
 * foreman_compute_resource: create and maintain compute resources
 * foreman_domain: create and maintain domains
 * foreman_environment: create and maintain environments (puppet)
 * foreman_config_group: create and maintain config groups (puppet)
 * foreman_global_parameter: create and maintain global parameters
 * foreman_hostgroup: create and maintain hostgroups
 * foreman_job_template: create and maintain job templates and associated template inputs
 * foreman_location: create and maintain locations
 * foreman_operating_system: create and maintain operating systems
 * foreman_organization: create and maintain organizations
 * foreman_os_default_template: create and maintain the association of default templates to operating systems
 * foreman_provisioning_template: create and maintain provisioning templates
 * foreman_ptable: create and maintain partition templates
 * foreman_role: create and maintain user roles
 * foreman_snapshot: create, modify, revert and delete snapshots
 * foreman_setting: set and reset settings
 * foreman_subnet: create and maintain subnets
 * katello_activation_key: create and maintain activation keys
 * katello_content_credential: create and maintain content credentials
 * katello_content_view: create and maintain content views
 * katello_product: create and maintain products
 * katello_repository: create and maintain repositories
 * katello_sync_plan: create and maintain sync plans
 * redhat_manifest: create and maintain manifests

#### Action Modules

 * katello_sync: sync Katello repositories and products
 * katello_upload: upload files, rpms, etc. to repositories. Note, rpms & files are idempotent.
 * katello_content_view_publish: publish Katello content views
 * katello_manifest: upload and Manage Katello manifests



## Ansible Version

Please note that you need Ansible >= 2.3 to use these modules.
As we're using Ansible's [documentation fragment](https://docs.ansible.com/ansible/devel/dev_guide/developing_modules_documenting.html#documentation-fragments) feature, that was introduced in Ansible 2.8, `ansible-doc` prior to 2.8 won't be able to display the module documentation, but the modules will still run fine with `ansible` and `ansible-playbook`.

## Python Version

Starting with Ansible 2.7, Ansible only supports Python 2.7 and 3.5 (and higher). These are also the only Python versions we develop and test the modules against.

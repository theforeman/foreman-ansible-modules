# Foreman Ansible Modules [![Build Status](https://travis-ci.org/theforeman/foreman-ansible-modules.svg?branch=master)](https://travis-ci.org/theforeman/foreman-ansible-modules)

This repository contains Ansible modules for interacting with a Foreman server API and various plugin APIs such as Katello.

## Goals

The intent of this repository is to be a place that community members can develop or contribute modules. The goals of this repository are:

  * centralized location for community modules
  * a single repository to clone for interacting with Foreman & plugins
  * an intermediate landing place for modules before pushing them to Ansible community
  * repository maintainers will be working to push the modules into Ansible proper [https://github.com/ansible/ansible/tree/devel/lib/ansible/modules/remote_management/foreman](https://github.com/ansible/ansible/tree/devel/lib/ansible/modules/remote_management/foreman)

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

## How to test modules in this repository

To test, you need a running instance of Foreman, probably with Katello (use [forklift](https://github.com/theforeman/forklift) if unsure).
Also you need to run `make test-setup` and update `test/test_playbooks/server_vars.yml`:

```sh
make test-setup
vi test/test_playbooks/server_vars.yml # point to your Foreman instance
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

See also [Guidedeline to writing tests](test/README.md).

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
./.tmp/ansible/hacking/test-module -m modules/katello_content_view.py -a @test/data/content-view.json -D /usr/lib64/python2.7/pdb.py
...
```

You can set a number of environment variables besides `MODULE` to configure make. Check the [Makefile](https://github.com/theforeman/foreman-ansible-modules/blob/master/Makefile) for more configuration options.

## Modules List

This is a list of modules currently in the repository (please add to the list if adding a module).

#### Entity Modules

 * foreman_global_parameter: create and maintain global parameters
 * foreman_operating_system: create and maintain operating systems
 * foreman_os_default_template: create and maintain the association of default templates to operating systems
 * foreman_organization: create and maintain organizations
 * foreman_location: create and maintain locations
 * foreman_ptable: create and maintain partition templates
 * foreman_provisioning_template: create and maintain provisioning templates
 * foreman_compute_resource: create and maintain compute resources
 * foreman_domain: create and maintain domains
 * foreman_subnet: create and maintain subnets
 * foreman_environment: create and maintain environments (puppet)
 * foreman_job_template: create and maintain job templates and associated template inputs
 * foreman_setting: set and reset settings
 * katello_content_credential: create and maintain content credentials
 * katello_product: create and maintain products
 * katello_repository: create and maintain repositories
 * katello_content_view: create and maintain content views
 * katello_sync_plan: create and maintain sync plans
 * katello_activation_key: create and maintain activation keys
 * redhat_manifest: create and maintain manifests

#### Action Modules

 * katello_sync: sync Katello repositories and products
 * katello_upload: upload files, rpms, etc. to repositories. Note, rpms & files are idempotent.
 * katello_content_view_publish: publish Katello content views
 * katello_manifest: upload and Manage Katello manifests

## Nailgun Versions

Below is listed the correct Nailgun branch for your Server

Server | Nailgun branch
------------ | -------------
Katello | master
Satellite 6.3 | 6.3.z
Satellite 6.2 | 6.2.z

## Ansible Version
Please note that you need ansible >= 2.3 to use these modules.

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

Now your playbooks and roles should have access to the modules and module_utils
contained in the repository for use, testing, or development of new modules.

## How to test modules in this repository

To test, you need a running instance of Foreman, probably with Katello (use [forklift](https://github.com/theforeman/forklift) if unsure).
Also you need to run test-setup and update test/test_playbooks/server_vars.yml:

```sh
make test-setup
vi test/test_playbooks/server_vars.yml # point to your Foreman instance
```

To run the tests:

```sh
make test # all tests
make test_product  # single test
make test TEST="-k 'organzation or product'"  # select tests by expression (see `pytest -h`)
```

The tests are run against prerecorded server-responses.
You can (re-)record the cassettes for a specific test with

```sh
make record_<test name>
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

### Katello/Foreman API modules

These are all API objects as of Foreman 1.17 and Katello 3.5 and their Ansible module in this repository, if available:

https://theforeman.org/plugins/katello/3.5/api/index.html  
https://theforeman.org/api/1.17/index.html

Some APIs are readonly, a foreman_facts/katello_facts module would ideally offer them all at once to Ansible.

- [x] Activation keys - [katello_activation_key](https://github.com/theforeman/foreman-ansible-modules/blob/master/modules/katello_activation_key.py)
- [ ] Architectures
- [ ] Audits - readonly
- [ ] Auth source ldaps
- [ ] Autosign
- [ ] Bookmarks
- [ ] Capsule content
- [ ] Capsules - readonly
- [x] Common parameters - [foreman_global_parameter](https://github.com/theforeman/foreman-ansible-modules/blob/master/modules/foreman_global_parameter.py)
- [ ] Compute attributes
- [x] Compute profiles - [foreman_compute_profile](https://github.com/theforeman/foreman-ansible-modules/blob/master/modules/foreman_compute_profile.py)
- [x] Compute resources - [foreman_compute_resource](https://github.com/theforeman/foreman-ansible-modules/blob/master/modules/foreman_compute_resource.py)
- [ ] Config groups
- [ ] Config reports
- [ ] Config templates
- [ ] Containers
- [ ] Content uploads
- [ ] Content view components
- [ ] Content view filter rules
- [ ] Content view filters
- [ ] Content view histories - readonly
- [ ] Content view puppet modules
- [ ] Content view versions
- [x] Content views - [katello_content_view](https://github.com/theforeman/foreman-ansible-modules/blob/master/modules/katello_content_view.py)
- [ ] Dashboard - readonly
- [ ] Docker manifests - readonly
- [ ] Docker tags - readonly
- [x] Domains - [foreman_domain](https://github.com/theforeman/foreman-ansible-modules/blob/master/modules/foreman_domain.py)
- [ ] Environments
- [ ] Errata - readonly
- [ ] External usergroups
- [ ] Fact values - readonly
- [ ] File units - readonly
- [ ] Filters
- [ ] Foreman tasks
- [ ] Gpg keys
- [ ] Home - readonly
- [ ] Host classes
- [ ] Host collections
- [ ] Host errata
- [ ] Host packages
- [ ] Host subscriptions
- [ ] Host tracer - readonly
- [ ] Hostgroup classes
- [ ] Hostgroups
- [ ] Hosts
- [ ] Hosts bulk actions
- [ ] Http proxies - Introduced in Foreman 1.17
- [ ] Images
- [ ] Interfaces
- [ ] Lifecycle environments
- [x] Locations - [foreman_location](https://github.com/theforeman/foreman-ansible-modules/blob/master/modules/foreman_location.py)
- [ ] Mail notifications - readonly
- [ ] Media
- [ ] Models
- [x] Operating systems - [foreman_operating_system](https://github.com/theforeman/foreman-ansible-modules/blob/master/modules/foreman_operating_system.py)
- [x] Organizations - [foreman_organization](https://github.com/theforeman/foreman-ansible-modules/blob/master/modules/foreman_organization.py)
- [x] Os default templates - [foreman_os_default_template](https://github.com/theforeman/foreman-ansible-modules/blob/master/modules/foreman_os_default_template.py)
- [ ] Ostree branches
- [ ] Override values
- [ ] Package groups
- [ ] Packages - readonly
- [ ] Parameters
- [ ] Permissions - readonly
- [ ] Ping - readonly
- [ ] Personal access tokens - Introduced in Foreman 1.17
- [ ] Plugins - readonly
- [x] Products - [katello_product](https://github.com/theforeman/foreman-ansible-modules/blob/master/modules/katello_product.py)
- [ ] Products bulk actions
- [x] Provisioning templates - [foreman_provisioning_template](https://github.com/theforeman/foreman-ansible-modules/blob/master/modules/foreman_provisioning_template.py)
- [x] Ptables - [foreman_ptable](https://github.com/theforeman/foreman-ansible-modules/blob/master/modules/foreman_ptable.py)
- [ ] Puppet hosts - Introduced in Foreman 1.17
- [ ] Puppet modules - readonly
- [ ] Puppetclasses
- [ ] Realms
- [ ] Recurring logics
- [ ] Registries
- [ ] Reports
- [x] Repositories - [katello_repository](https://github.com/theforeman/foreman-ansible-modules/blob/master/modules/katello_repository.py)
- [ ] Repositories bulk actions
- [ ] Repository sets
- [ ] Roles
- [ ] Settings
- [ ] Smart class parameters
- [ ] Smart proxies
- [ ] Smart variables
- [ ] Ssh keys
- [ ] Statistics - readonly
- [ ] Subnets
- [ ] Subscriptions
- [ ] Sync - readonly
- [x] Sync plans - [katello_sync_plan](https://github.com/theforeman/foreman-ansible-modules/blob/master/modules/katello_sync_plan.py)
- [ ] Tasks - readonly
- [ ] Template combinations
- [ ] Template kinds - readonly
- [ ] Usergroups
- [ ] Users

### Non-Katello/Foreman API modules

These modules are not directly interacting with Foreman/Katello, but are in some case necessary as input or prerequisite for other modules.

 * [redhat_manifest](https://github.com/theforeman/foreman-ansible-modules/blob/master/modules/redhat_manifest.py): create and maintain manifests

### Action Modules

These modules are not idempotent and will always cause a change on the target host.

 * [katello_sync](https://github.com/theforeman/foreman-ansible-modules/blob/master/modules/katello_sync.py): sync Katello repositories and products
 * [katello_upload](https://github.com/theforeman/foreman-ansible-modules/blob/master/modules/katello_upload.py): upload files, rpms, etc. to repositories
 * [katello_content_view_publish](https://github.com/theforeman/foreman-ansible-modules/blob/master/modules/katello_content_view_publish.py): publish Katello content views
 * [katello_manifest](https://github.com/theforeman/foreman-ansible-modules/blob/master/modules/katello_manifest.py): upload and Manage Katello manifests

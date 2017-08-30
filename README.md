# Foreman Ansible Modules [![Build Status](https://travis-ci.org/theforeman/foreman-ansible-modules.svg?branch=master)](https://travis-ci.org/theforeman/foreman-ansible-modules)

This repository contains Ansible modules for interacting with a Foreman server API and various plugin APIs such as Katello.

## Goals

The intent of this repository is to be a place that community members can develop or contribute modules. The goals of this repository are:

  * centralized location for community modules
  * a single repository to clone for interacting with Foreman
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

## How to debug this repository

Set up debugging using ansible's test-module

```sh
ansible-playbook debug-setup.yml
```

Debug with ansible's test-module

```sh
./ansible/hacking/test-module -m <path to ansible module> -a @<path to input arguments to module> -D <path to debugger>

# Example: debug the activation_key module with pdb
./ansible/hacking/test-module -m ./foreman-ansible-modules/modules/katello_activation_key.py -a @activation-key-args.json -D /usr/lib/python2.7/site-packages/pdb/pdb.py
```

## Modules List

This is a list of modules currently in the repository (please add to the list if adding a module).

#### Entity Modules

 * foreman_global_parameter: create and maintain global parameters
 * foreman_operating_system: create and maintain operating systems
 * foreman_organization: create and maintain organizations
 * foreman_ptable: create and maintain partition templates
 * foreman_provisioning_template: create and maintain provisioning templates
 * foreman_compute_resource: create and maintain compute resources
 * katello_product: create and maintain products
 * katello_repository: create and maintain repositories
 * katello_content_view: create and maintain content views
 * katello_sync_plan: create and maintain sync plans
 * katello_activation_key: create and maintain activation keys

#### Action Modules

 * katello_sync: sync Katello repositories and products
 * katello_upload: upload files, rpms, etc. to repositories
 * katello_publish: publish Katello content views

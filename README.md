# Foreman Ansible Modules

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

Now, add or update your `ansible.cfg` file to include the modules path:

```
cat ansible.cfg

[defaults]
library = foreman-ansible-modules/modules
```

Now your playbooks and roles should have access to the modules contained in the repository for use, testing or development of new modules.

## Modules List

This is a list of modules currently in the repository (please add to the list if adding a module).

### Entity Modules

 * foreman_organization: create and maintain organizations
 * katello_product: create and maintain products
 * katello_repository: create and maintain repositories

### Action Modules

 * katello_sync: sync Katello repositories and products
 * katello_upload: upload files, rpms, etc. to repositories
 * katello_publish: publish Katello content views

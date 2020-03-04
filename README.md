# Foreman Ansible Modules ![Build Status](https://github.com/theforeman/foreman-ansible-modules/workflows/CI/badge.svg)

Ansible modules for interacting with the Foreman API and various plugin APIs such as Katello.

## Documentation

A list of all modules and their documentation can be found at [theforeman.org/plugins/foreman-ansible-modules](https://theforeman.org/plugins/foreman-ansible-modules/).

Documentation how to [write](docs/developing.md) and [test](docs/testing.md) modules is available in the [`docs`](docs/) folder.

## Support

### Supported Foreman and plugins versions

Modules should support any currently stable Foreman release and the matching set of plugins.
Some modules have additional features/arguments that are only applied when the corresponding plugin is installed.

We actively test the modules against the latest stable Foreman release and the matching set of plugins.

### Supported Ansible Versions

The supported Ansible versions are aligned with currently maintained ansible versions. You can find the list of maintained Ansible versions [here](https://docs.ansible.com/ansible/latest/reference_appendices/release_and_maintenance.html#release-status). Older Ansible versions (Ansible >= 2.3) should work but are not tested.

As we're using Ansible's [documentation fragment](https://docs.ansible.com/ansible/devel/dev_guide/developing_modules_documenting.html#documentation-fragments) feature, that was introduced in Ansible 2.8, `ansible-doc` prior to 2.8 won't be able to display the module documentation, but the modules will still run fine with `ansible` and `ansible-playbook`.

### Supported Python Versions

Starting with Ansible 2.7, Ansible only supports Python 2.7 and 3.5 (and higher). These are also the only Python versions we develop and test the modules against.

### Known issues

* Some modules, e.g. `katello_sync` and `katello_content_view_version`, trigger long running tasks on the server side. It might be beneficial to your playbook to wait for their completion in an asynchronous manner.
  As Ansible has facilities to do so, the modules will wait unconditionally. See the [Ansible documentation](https://docs.ansible.com/ansible/latest/user_guide/playbooks_async.html) for putting tasks in the background.

* `foreman_compute_resource` leak sensible data if used within a loop. According to [ansible documentation](https://docs.ansible.com/ansible/latest/user_guide/playbooks_loops.html), using loop over ansible resources can leak sensible data. You can prevent this by using `no_log: yes` on the task.
  
  eg:
   ```yaml
   - name: Create compute resources
     foreman_compute_resource:
       server_url: https://foreman.example.com
       username: admin
       password: changeme
       validate_certs: yes
       name: "{{ item.name }}"
       organizations: "{{ item.organizations | default(omit) }}"
       locations: "{{ item.locations | default(omit) }}"
       description: "{{ item.description | default(omit) }}"
       provider: "{{ item.provider }}"
       provider_params: "{{ item.provider_params | default(omit) }}"
       state: "{{ item.state | default('present') }}"
     loop: "{{ compute_resources }}"
     no_log: yes
   ```

## Installation

There are currently three ways to use the modules in your setup: install from Ansible Galaxy, install via RPM and run directly from Git.

### Installation from Ansible Galaxy

You can install the collection from [Ansible Galaxy](https://galaxy.ansible.com/theforeman/foreman) by running `mazer install theforeman.foreman` (Ansible 2.8) or `ansible-galaxy collection install theforeman.foreman` (Ansible 2.9 and later).

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

These dependencies are required for the Ansible controller, not the Foreman server. 

* `PyYAML`
* [`apypie`](https://pypi.org/project/apypie/)
* [`ipaddress`](https://pypi.org/project/ipaddress/) for the `foreman_subnet` module on Python 2.7

## Branches

* `master` - current development branch, using the `apypie` library
* `nailgun` - the state of the repository before the switch to the `apypie` library started, `nailgun` is the only dependency

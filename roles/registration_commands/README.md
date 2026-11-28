theforeman.foreman.registration_command
===========================

Generate Registration Command

Role Variables
--------------

This role supports the [Common Role Variables](https://github.com/theforeman/foreman-ansible-modules/blob/develop/README.md#common-role-variables).

- `foreman_organization`: Organization to register the host in.
- `foreman_location`: Location to register the host in.
- `foreman_hostgroup`: Host group to register the host in.
- `foreman_operatingsystem`: Operating System to register the host in, operating system must have a `host_init_config` template assigned.
- `foreman_smart_proxy`: Register host through smart proxy.
- `foreman_insecure`: Enable insecure argument for the initial curl.
- `foreman_setup_remote_execution`: Set `host_registration_remote_execution` parameter for the host. If it is set to `true`, SSH keys will be installed on the host.
- `foreman_setup_insights`: Set `host_registration_insights` parameter for the host. If it is set to `true`, insights client will be installed and registered on Red Hat family operating systems.
- `foreman_packages`: Packages to install on the host when registered, example: `pkg1 pkg2`
- `foreman_update_packages`: Update all packages on the host.
- `foreman_repo`: Repository URL / details, for example for Debian OS family: 'deb http://deb.example.com/ buster 1.0', for Red Hat OS family: 'http://yum.theforeman.org/client/latest/el8/x86_64/'.
- `foreman_repo_gpg_key_url`: URL of the GPG key for the repository.
- `foreman_jwt_expiration`: Expiration of the authorization token (in hours).
- `foreman_remote_execution_interface`: Identifier of the Host interface for Remote execution.
- `foreman_activation_keys`: Activation keys for subscription-manager client, required for CentOS and Red Hat Enterprise Linux. Required only if host group has no activation keys.
- `foreman_lifecycle_environment`: Lifecycle environment for the host.
- `foreman_ignore_subman_errors`: Ignore subscription-manager errors for `subscription-manager register` command.
- `foreman_force`: Clear any previous registration and run subscription-manager with --force.

Example Playbooks
-----------------

Generate registration command

```yaml
- hosts: localhost
  roles:
    - role: theforeman.foreman.registration_commands
      vars:
        foreman_server_url: "https://foreman.example.com"
        foreman_username: "admin"
        foreman_password: "changeme"
        foreman_organization: "Default Organization"
```

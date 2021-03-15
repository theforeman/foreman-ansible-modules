# users

## This role can be used to create users, user groups, LDAP-Auth and to link external and internal user groups

### You can disable certain tasks

#### Tasks to switch on/off

+ foreman_create_users
+ foreman_create_usergroups
+ foreman_enable_ldap_auth
+ foreman_map_external_usergroups

### Role Variables

Default:

``` yaml
foreman_server_url: string(url) **required**
foreman_username: string **required**
foreman_password: string
foreman_password: string
foreman_validate_certs: bool default (true)
```

To switch on/off tasks use:

``` yaml
foreman_create_users: bool default (true)
foreman_create_usergroups: bool default (true)
foreman_enable_ldap_auth: bool default (true)
foreman_map_external_usergroups: bool default (true)
```

For user creation use:

``` yaml
foreman_users:
  - username: string **required**
    firstname: string
    lastname: string
    email: string(email)
    description: string
    admin_rights: bool
    user_password: string **required when internal**
    default_location: string
    default_organization: string
    auth_source: string **required**
    timezone: string
    user_locale: string
    roles:
      - string
    locations:
      - string
    organizations:
      - string
```

For usergroup creation use:

``` yaml
foreman_usergroups:
  - usergroupname: string **required**
    admin_rights: bool
    roles:
      - string # can be found in Webui
    users:
      - string
    usergroups: string  # nested group
```

For LDAP auth

``` yaml
foreman_auth_sources:
  - ldap_name: string **required**
    port: int # default port 389 is set
    ldap_host: string **required**
    onthefly_register: bool
    ldap_account: string
    ldap_password: string
    ldap_base_dn: string
    ldap_groups_base: string
    ldapserver_type: string
    attr_login: string
    attr_firstname: string
    attr_lastname: string
    attr_mail: string
    attr_photo: string
```

For linking external groups with internal groups

``` yaml
foreman_linked_usergroups:
  external_usergroupname: string **required**
  foreman_usergroup: string **required**
  auth_source_ldap: string **required**
```

To suppress log use

``` yaml
foreman_users_hide_log: bool default (true)
```

### Usage

+ First install the theforeman-collection for example as a package:

```yum install -y ansible-collection-theforeman-foreman.noarch```

+ Clone / get this role

```git clone ............```

### Requirements

+ ansible collection theforeman.foreman
  + PyYAML
  + apypie

### Example Playbook

``` yaml
---
- hosts: orcharhinos
  vars:
    foreman_server_url: https://orcharhino.fqdn
    foreman_username: admin
    foreman_password: password
    foreman_organization: organization
    foreman_location: World
    foreman_create_users: false
    foreman_create_usergroups: false
    foreman_enable_ldap_auth: false
    foreman_map_external_usergroups: false
    foreman_users_hide_log: true
  roles:
     - { role: users }
  gather_facts: no
```

## License

GPL

## Author Information

Richard Stempfl

Atix AG

atix.de orcharhino.de

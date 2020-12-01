# or_usermanagement

## This role can be used to create users, user groups, LDAP-Auth and to link external and internal user groups

### You can disable certain tasks

#### Tasks to switch on/off

+ create_users
+ create_usergroups
+ enable_ldap_auth
+ map_external_usergroups

### Role Variables

#### Example values can be found in defaults/main.yaml

Default:

``` yaml
server_url: string(url) **required**
username: string **required**
password: string
password: string
validate_certs: bool defualt (true)
```

To switch on/off tasks use:

``` yaml
create_users: bool defualt (true)
create_usergroups: bool defualt (true)
enable_ldap_auth: bool defualt (true)
map_external_usergroups: bool defualt (true)
```

For user creation use:

``` yaml
or_users:
  - username: string **required**
    firstname: string
    lastname: string
    email: string(email)
    description: string
    admin_rights: bool
    user_password: string **required when internal**
    default_location: string
    default_organization: string
    auth_source: sting **required**
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
or_usergroups:
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
ldap_name: string **required**
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
linked_groups:
  external_usergroupname: string **required**
  or_usergroup: string **required**
  auth_source_ldap: string **required**
```

## Usage

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
    or_url: https://orcharhino.fqdn
    or_admin_user: admin
    or_admin_password: password
    or_organization: organization
    or_location: World
    create_users: false
    create_usergroups: false
    enable_ldap_auth: false
    map_external_usergroups: false
  roles:
     - { role: or_usermanagement }
  gather_facts: no
```

## License

GPL

## Author Information

Richard Stempfl

Atix AG

atix.de orcharhino.de

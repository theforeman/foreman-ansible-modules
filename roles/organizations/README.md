# theforeman.foreman.organizations

## Description
An Ansible Role to create Organizations in Foreman.

Role Variables
--------------

This role supports the [Common Role Variables](https://github.com/theforeman/foreman-ansible-modules/blob/develop/README.md#common-role-variables).

- `foreman_organizations`: list of organizations to manage. See Variables table below for data structure definition. Default is `[]`.

### Organization Data Structure
|Variable Name|Default Value|Required|Description|
|:---:|:---:|:---:|:---:|
|`name`|" "|yes|Name of Organization.|
|`description`|" "|no|Description of Named Organization.|
|`label`|" "|no|Label of the Organization.|
|`state`|`present`|no|Desired State of the Entity.|

## Playbook Examples
### Standard Role Usage
```yaml
--- 
- name: add organizations to foreman
  hosts: localhost
  gather_facts: false
  tasks:
    - name: add organizations
      include_role: 
        name: theforeman.foreman.organizations
      vars: 
            foreman_server_url: https://foreman.example.com
            foreman_username: admin
            foreman_password: changeme
            foreman_organizations: 
              - name: raleigh
                label: rdu
                state: present
              - name: default
                label: boring
                state: absent
              - name: lanai 
                description: pacific datacenter 
```
## Author
[Chris Hindman](https://github.com/hindman-redhat)

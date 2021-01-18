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

### Secure Logging Variables
The following Variables compliment each other.
If both variables are not set, secure logging defaults to false.
The role defaults to False as normally the add organization task does not include sensitive information.
`foreman_configuration_organizations_secure_logging` defaults to the value of `foreman_configuration_secure_logging` if it is not explicitly called. This allows for secure logging to be toggled for the entire suite of configuration roles with a single variable, or for the user to selectively use it.

|Variable Name|Default Value|Required|Description|
|:---:|:---:|:---:|:---:|
|`foreman_configuration_organizations_secure_logging`|`False`|no|Whether or not to include the sensitive Organization role tasks in the log.  Set this value to `True` if you will be providing your sensitive values from elsewhere.|
|`forman_configuration_secure_logging`|`False`|no|This variable enables secure logging as well, but is shared across multiple roles, see above.|

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

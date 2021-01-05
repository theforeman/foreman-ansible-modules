# theforeman.foreman.organizations

## Description
An Ansible Role to create Organizations in Foreman.

## Variables
|Variable Name|Default Value|Required|Description|Example|
|:---:|:---:|:---:|:---:|:---:|
|`foreman_server_url`|""|no|URL of the Foreman server.|
|`foreman_username`|""|no|Username accessing the Foreman Server.|
|`foreman_password`|""|no|Password of user accessing the Foreman Server.  This should be stored at vars/foreman-secrets.yml or elsewhere.|
|`foreman_prefix` |"foreman_"|no|Whether or not to verify the TLS certificates of the Foreman server.|

### Secure Logging Variables
The following Variables compliment each other.
If both variables are not set, secure logging defaults to false.
The role defaults to False as normally the add organization task does not include sensitive information.
foreman_configuration_organizations_secure_logging defaults to the value of foreman_configuration_secure_logging if it is not explicitly called. This allows for secure logging to be toggled for the entire suite of configuration roles with a single variable, or for the user to selectively use it.

|Variable Name|Default Value|Required|Description|
|:---:|:---:|:---:|:---:|
|`foreman_configuration_organizations_secure_logging`|`False`|no|Whether or not to include the sensitive Organization role tasks in the log.  Set this value to `True` if you will be providing your sensitive values from elsewhere.|
|`forman_configuration_secure_logging`|`False`|no|This variable enables secure logging as well, but is shared across multiple roles, see above.|

## Organization Data Structure
This role accepts two data models. A simple straightforward easy to maintain model, and another based on the tower api. The 2nd one is more complicated and includes more detail, and is compatiable with tower import/export.

### Variables
|Variable Name|Default Value|Required|Description|
|:---:|:---:|:---:|:---:|
|`name`|""|yes|Name of Organization.|
|`description`|""|no|Description of Named Organization.|
|`label`|``|no|Custom Label.|
|`state`|`present`|no|Desired State of the Resource.|

## Playbook Examples
### Standard Role Usage
```yaml
--- 
- name: add organizations to foreman
  hosts: localhost
  connection: local
  gather_facts: false
  vars_files: 
    - ../tests/vars/foreman_secrets.yml
  tasks:
    - name: add organizations
      include_role: 
        name: ../..
      vars: 
            foreman_server_url: url
            foreman_username: user
            foreman_password: pass
            foreman_validate_certs: no
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
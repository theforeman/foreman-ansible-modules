theforeman.foreman.content_views
=========================================

This role creates and manages Content Views.

Role Variables
--------------

This role supports the [Common Role Variables](https://github.com/theforeman/foreman-ansible-modules/blob/develop/README.md#common-role-variables).

The main data structure for this role is the list of `foreman_content_views`. Each Content View requires the following fields:

- `name`
- `content_view`
- `content_view_update`
- `repos`
  - `name`
  - `product`
  - `basearch`: (optional)
  - `releasever`: (optional)

The following fields are optional and will be omitted by default:

- `filters`

### Secure Logging Variables
The following Variables compliment each other.
If both variables are not set, secure logging defaults to false.
The role defaults to False as normally the add content view task does not include sensitive information.
`foreman_configuration_content_views_secure_logging` defaults to the value of `foreman_configuration_secure_logging` if it is not explicitly called. This allows for secure logging to be toggled for the entire suite of configuration roles with a single variable, or for the user to selectively use it.

|Variable Name|Default Value|Required|Description|
|:---:|:---:|:---:|:---:|
|`foreman_configuration_content_views_secure_logging`|`False`|no|Whether or not to include the sensitive content view role tasks in the log.  Set this value to `True` if you will be providing your sensitive values from elsewhere.|
|`forman_configuration_secure_logging`|`False`|no|This variable enables secure logging as well, but is shared across multiple roles, see above.|

Example Playbooks
-----------------

```yaml
- hosts: localhost
  roles:
    - role: theforeman.foreman.content_views
      vars:
        server_url: https://foreman.example.com
        username: "admin"
        password: "changeme"
        organization: "Default Organization"
        foreman_content_views:
          - name: RHEL7
            content_view: RHEL7
            content_view_update: true
            repos:
            - name: Red Hat Enterprise Linux 7 Server (RPMs)
              basearch: x86_64
              releasever: 7Server
              product: 'Red Hat Enterprise Linux Server'
            - name: Red Hat Enterprise Linux 7 Server - Extras (RPMs)
              basearch: x86_64
              product: 'Red Hat Enterprise Linux Server'
            - name: Red Hat Satellite Tools 6.8 (for RHEL 7 Server) (RPMs)
              basearch: x86_64
              product: 'Red Hat Enterprise Linux Server'
```
